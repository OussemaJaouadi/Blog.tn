
from datetime import timedelta
from flask import Flask, jsonify, make_response, render_template, render_template_string, url_for, flash, redirect, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from auth import require_role,get_user_from_token,gen_token,SECRET_KEY,PORT
from forms import RegistrationForm, LoginForm, UpdateAccountForm,PostForm,UpdatePost
from models import User, Post,Base


app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=3)
app.secret_key = SECRET_KEY
engine = create_engine('sqlite:///database.db')
Session = sessionmaker(bind=engine)

def clear_token_cookie():
    print("Clearing token cookie...")
    resp = make_response(redirect(url_for('home')))
    resp.set_cookie('token', '', expires=0)
    print("Token cookie cleared!")
    return resp



notifications = [{
    'title':'{7*7}',
    'message':'test account'
}]

@app.route("/")
@app.route("/home")
def home():
    current_user, _ = get_user_from_token()
    session = Session()
    
    if current_user and _ == 'admin':
        # If logged in user is admin, show all posts
        posts = session.query(Post).all()
    elif current_user:
        # If logged in user is regular user, show only their own posts
        user = session.query(User).filter_by(username=current_user).first()
        posts = session.query(Post).filter_by(author=user).all()
    else:
        # If not logged in, show all published posts
        posts = session.query(Post).filter_by(published=True).all()
        if not posts:
            return render_template('error.html',code="empty",message="No posts yet")

    return render_template('home.html', title='Home', posts=posts, user=current_user)


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    current_user,_ = get_user_from_token()
    if current_user:
        flash('You are already log in', 'success')
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        session = Session()
        tmp = session.query(User).filter_by(username=form.username.data).first()
        if tmp:
            session.close()
            flash('Your username already exists', 'danger')
            return render_template('register.html', title='Register', form=form)
        try :
            user = User(username=form.username.data,password=form.password.data)
            session.add(user)
            session.commit()
            session.close()
            flash('Your account has been created! You are now able to log in', 'success')
            return redirect(url_for('login'))
        except IntegrityError :
            print("an error occurred")
            return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form,user=None)


@app.route("/login", methods=['GET', 'POST'])
def login():
    current_user,_ = get_user_from_token()
    if current_user:
        flash('You are already log in', 'success')
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        session = Session()
        user = session.query(User).filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            token = gen_token(user.username,"user")
            response = make_response(redirect(url_for('home')))
            response.set_cookie('token',token)
            return response
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form,user=None)


@app.route('/logout')
def logout():
    response = make_response(redirect(url_for('login')))
    response.delete_cookie('token')
    return response



@app.route("/account", methods=['GET', 'POST'])
@require_role(['user','admin'])
def account():
    username, _ = get_user_from_token()
    session = Session()
    user = session.query(User).filter_by(username=username).first()

    form = UpdateAccountForm(obj=user)

    if form.validate_on_submit():
        if user.username != form.username.data:
            # Check if new username is already taken
            if session.query(User).filter_by(username=form.username.data).first():
                flash('Username already taken. Please choose a different one.', 'danger')
                return redirect(url_for('account'))

        form.populate_obj(user)
        session.commit()
        flash('Profile updated successfully!', 'success')
        response = make_response(redirect(url_for('account')))
        response.delete_cookie('token')
        newToken = gen_token(user.username,_)
        response.set_cookie('token',newToken) 
        return response

    if _ == 'admin':
        posts = session.query(Post).all()
    else : 
        posts = session.query(Post).filter_by(author=user).all()
    return render_template('account.html', form=form, current_user=username,role=_,posts=posts)

@app.route("/addpost", methods=['GET', 'POST'])
@require_role(['user','admin'])
def addpost():
    current_user, _ = get_user_from_token()
    form = PostForm()

    if form.validate_on_submit():
        session = Session()

        # Check if the post title already exists
        post = session.query(Post).filter_by(title=form.title.data).first()
        if post:
            flash('A post with that title already exists.', 'danger')
            return redirect(url_for('addpost'))
        
        user = session.query(User).filter_by(username=current_user).first()
        post = Post(title=form.title.data, details=form.details.data, category=form.category.data, author=user)
        session.add(post)
        session.commit()
        flash('Post created successfully!', 'success')
        return redirect(url_for('home'))

    return render_template('addpost.html',title="Add Post", form=form,user=current_user)

@app.route('/editpost/<int:id>', methods=['GET', 'POST'])
@require_role(['user','admin'])
def editpost(id):
    session = Session()
    post = session.query(Post).filter_by(id=id).first()
    if post is None:
        return render_template('error.html', code="404", message="Post not found")
    current_user, _ = get_user_from_token()
    if not _ == "admin" or not current_user == post.author.username:
        return render_template('error.html', code="403", message="Not Your Post to edit")
    form = UpdatePost(obj=post)
    if form.validate_on_submit():
        post.title = form.title.data
        post.category = form.category.data
        post.details = form.details.data
        post.published = form.is_published.data
        session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('editpost', id=post.id))
    return render_template('editpost.html', title='Update Post', form=form, post=post,user=current_user)



@app.route('/deletepost/<int:id>', methods=['GET'])
@require_role(['user','admin'])
def deletepost(id):
    session = Session()
    post = session.query(Post).filter_by(id=id).first()
    if post is None:
        return render_template('error.html', code="404", message="Post not found")
    current_user, _ = get_user_from_token()
    if not _ == "admin" or not current_user == post.author.username:
        return render_template('error.html', code="403", message="Not Your Post to edit")
    session.delete(post)
    session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('home'))

@app.route('/notifications')
def show_notifications():
    current_user, _ = get_user_from_token()
    return render_template('notifications.html', notifications=notifications,user=current_user)

# Create a new notification
@app.route('/createNotif', methods=['GET', 'POST'])
def create_notification():
    current_user, _ = get_user_from_token()
    if request.method == 'POST':
        title = request.form['title']
        message = request.form['message']

        # Add the new notification to the notifications list
        notifications.append({'title': title, 'message': message})
        success = '''
        Your Notificiation "{}" has been created
        '''.format(title)
        tmpl = render_template_string(success, title = title)
        return render_template('create_notification.html',user=current_user,success=tmpl)

    return render_template('create_notification.html',user=current_user)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html',code="404",message="Url Not Found")


if __name__ =='__main__' :
    Base.metadata.create_all(engine)
    app.run(debug=True,host="0.0.0.0",port=PORT)