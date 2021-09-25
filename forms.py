"""Forms for the Commentator app. There are forms for registering users, logging in users, editing users,
adding feedback, and editing feedback."""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Length, Email

class RegisterForm(FlaskForm):
    """A form used for registering a new user."""
    username=StringField("Username (max 30 characters)", validators=
    [InputRequired(message="Username required."), Length(max=30, 
    message="Username must be 30 characters or less.")])
    password=PasswordField("Password", validators=[InputRequired("Password required.")])
    email=StringField("Email (max 50 characters)", validators=
    [InputRequired("Email required."), Email(), Length(max=50, message="Email must be 50 characters or less.")])
    first_name=StringField("First Name (max 30 characters)", validators=
    [InputRequired("First name required."), Length(max=30, message="First name must be 30 characters or less.")])
    last_name=StringField("Last Name (max 30 characters)", validators=
    [InputRequired("Last name required."), Length(max=30, message="Last name must be 30 characters or less.")])

class LoginForm(FlaskForm):
    """A form used for logging a user in to the application."""
    username=StringField("Username (max 30 characters)", validators=[InputRequired(), Length(max=30, 
    message="Username must be 30 characters or less")])
    password=PasswordField("Password", validators=[InputRequired()])

class FeedbackForm(FlaskForm):
    """A form used for editing or adding feedback."""
    title=StringField("Title (max 100 characters)", validators=[InputRequired("Title required"), 
    Length(max=30, message="Title must be 100 characters or less.")])
    content=StringField("Content", validators=[InputRequired("Content required.")])