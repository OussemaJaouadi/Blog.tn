
import datetime
from sqlalchemy import Boolean, DateTime, ForeignKey, create_engine, Column, Integer, String,Date,Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from werkzeug.security import generate_password_hash, check_password_hash


Base = declarative_base()

class Post(Base):
    __tablename__ = 'post'

    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False, unique=True)
    details = Column(Text, nullable=False)
    category = Column(String(100), nullable=False)
    author_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    author = relationship('User', backref='posts', lazy='joined')
    date = Column(DateTime, default=datetime.date.today())
    published = Column(Boolean, default=False)

    def __init__(self, title, details, category, author):
        self.title = title
        self.details = details
        self.category = category
        self.author = author
        self.date = datetime.date.today()
        self.published = False




class User(Base):
    __tablename__ = 'user'
    id = Column(Integer , primary_key=True)
    username = Column(String(20) , unique=True , nullable=False)
    password = Column(String(128) , nullable=False)
    # posts = relationship('Post', backref='author', lazy=True)

    def __init__(self, username, password):
        self.username = username
        self.set_password(password) 

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    
