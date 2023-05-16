
from flask_wtf import FlaskForm
from wtforms import  StringField, PasswordField, SubmitField, BooleanField,TextAreaField,SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo , ValidationError
from models import User
from flask_wtf.file import FileField , FileAllowed

class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField('Username',
                        validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])

    submit = SubmitField('Update Profile')


class PostForm(FlaskForm):
    title = StringField('Title',validators=[DataRequired()])
    details = TextAreaField('Details', validators=[DataRequired()])
    category = SelectField('Category', choices=[('politics', 'Politics'), ('it', 'IT'), ('sports', 'Sports'),('entertainment','Entertainment')], validators=[DataRequired()])
    submit = SubmitField('Submit')    

class UpdatePost(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    details = TextAreaField('Details', validators=[DataRequired()])
    category = SelectField('Category', choices=[('politics', 'Politics'), ('it', 'IT'), ('sports', 'Sports'), ('entertainment', 'Entertainment')], validators=[DataRequired()])
    is_published = BooleanField('Publish Post')
    submit = SubmitField('Submit')
 
