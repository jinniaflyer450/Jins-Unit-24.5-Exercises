"""Models for users and feedback for the Commentator app."""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app import app
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

def connect_db(app):
    """An function that connects the app in 'app.py' to the application's database."""
    db.app = app
    db.init_app(app)

class User(db.Model):
    __tablename__ = "users"

    username=db.Column(db.String(20), primary_key=True)
    password=db.Column(db.Text, nullable=False)
    email=db.Column(db.String(50), nullable=False, unique=True)
    first_name=db.Column(db.String(30), nullable=False)
    last_name=db.Column(db.String(30), nullable=False)

    @classmethod
    def register(cls, username, password, email, first_name, last_name):
        hashed_password = bcrypt.generate_password_hash(password)
        utf8_hash = hashed_password.decode("utf8")
        
        return cls(username=username, password=utf8_hash, email=email, 
        first_name=first_name, last_name=last_name)