"""Commentator: An app where users can register, log in to their accounts, and log out. 
While they are logged in, they can submit, edit, and delete feedback, 
as well as updating or deleting their own accounts."""

from flask import Flask, render_template, redirect, flash, session
from flask_sqlalchemy import SQLAlchemy
from models import db, connect_db, User
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = 'catdog'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Ob1wankenobi@localhost/auth_practice'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

connect_db(app)
db.create_all()

@app.route('/')

@app.route('/register', methods=["GET", "POST"])

@app.route('/login', methods=["GET", "POST"])

@app.route('/secret')