"""Commentator: An app where users can register, log in to their accounts, and log out. 
While they are logged in, they can submit, edit, and delete feedback, 
as well as updating or deleting their own accounts."""

from flask import Flask, render_template, redirect, flash, session
from flask_sqlalchemy import SQLAlchemy
from models import db, connect_db, User
from forms import RegisterForm
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
def redirect_register():
    return redirect('/register')

@app.route('/register', methods=["GET", "POST"])
def register_user():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        
        new_user = User.register(username=username, password=password, email=email, 
        first_name=first_name, last_name=last_name)

        db.session.add(new_user)
        db.session.commit()
        
        flash("Successfully registered!")
        return redirect('/secret')
    return render_template('register.html', form=form)

@app.route('/login', methods=["GET", "POST"])

@app.route('/secret')