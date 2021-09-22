"""Commentator: An app where users can register, log in to their accounts, and log out. 
While they are logged in, they can submit, edit, and delete feedback, 
as well as updating or deleting their own accounts."""

from flask import Flask, render_template, redirect, flash, session
from flask_sqlalchemy import SQLAlchemy
from models import db, connect_db, User
from forms import RegisterForm, LoginForm
import requests
from sqlalchemy.exc import IntegrityError

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
    """A view function that redirects to the '/register' route."""
    return redirect('/register')

@app.route('/register', methods=["GET", "POST"])
def register_user():
    """A view function that returns 'register.html' on a GET request and attempts to register a new
    user on a POST request. If registration is successful, it returns a redirect to '/secret'. If not,
    it renders 'register.html' again with relevant errors."""
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

        #Handles the case where a user attempts to register with a duplicate username.
        try:
            db.session.commit()
        except IntegrityError:
            form.username.errors.append("Username already taken. Please choose another.")
            db.session.rollback()
            return render_template('register.html', form=form)

        flash("Successfully registered!")
        session["user_id"] = new_user.username
        return redirect('/secret')
    return render_template('register.html', form=form)

@app.route('/login', methods=["GET", "POST"])
def login_user():
    """A view function that returns 'login.html' on a GET request and attempts to log a user in on a 
    POST request. If login is successful, it returns a redirect to '/secret'. If not, it returns
    'login.html' again with relevant errors."""
    form=LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)

        if user:
            session["user_id"]=user.username
            flash("Logged in!")
            return redirect('/secret')
        else:
            form.username.errors.append("Incorrect username/password combination.")
    return render_template('login.html', form=form)

@app.route('/secret')
def secret_route():
    """A view function that confirms a user has successfully registered or logged in by returning
    'You made it!'"""
    return "You made it!"