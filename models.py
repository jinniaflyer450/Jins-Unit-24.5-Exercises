"""Models for users and feedback for the Commentator app."""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

def connect_db(app):
    """An function that connects the app in 'app.py' to the application's database."""
    db.app = app
    db.init_app(app)

class User(db.Model):
    """A user of the Commentator app."""
    __tablename__ = "users"

    username=db.Column(db.String(20), primary_key=True)
    password=db.Column(db.Text, nullable=False)
    email=db.Column(db.String(50), nullable=False, unique=True)
    first_name=db.Column(db.String(30), nullable=False)
    last_name=db.Column(db.String(30), nullable=False)

    @classmethod
    def register(cls, username, password, email, first_name, last_name):
        """A class method on the User model that returns an instance of the User class
        with a hashed password."""

        hashed_password = bcrypt.generate_password_hash(password)
        utf8_hash = hashed_password.decode("utf8")

        return cls(username=username, password=utf8_hash, email=email, 
        first_name=first_name, last_name=last_name)
    
    @classmethod
    def authenticate(cls, username, password):
        """A class method on the User model that checks an entered username and password
        against any username that matches the entered username in the database and its password.
        If the username exists in the database and its user's hashed password matches the hash in the
        database, the method returns the instance of the user. If either condition is not true, the
        method returns False"""
        
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            return user
        else:
            return False


class Feedback(db.Model):
    """A comment in the Commentator app."""
    __tablename__ = "feedback"

    id=db.Column(db.Integer, primary_key=True, autoincrement=True)
    title=db.Column(db.String(100), nullable=False)
    content=db.Column(db.Text, nullable=False)
    username=db.Column(db.String(20), db.ForeignKey("users.username"), nullable=False)

    user = db.relationship("User", backref="feedback")