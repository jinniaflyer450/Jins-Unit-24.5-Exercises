"""Forms for the Commentator app. There are forms for registering users, logging in users, editing users,
adding feedback, and editing feedback."""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from app import app