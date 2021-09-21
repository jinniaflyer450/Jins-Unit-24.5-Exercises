"""Models for users and feedback for the Commentator app."""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app import app

db = SQLAlchemy()

def connect_db(app):
    """An function that connects the app in 'app.py' to the application's database."""
    db.app = app
    db.init_app(app)