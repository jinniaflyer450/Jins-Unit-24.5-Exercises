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
        return redirect(f'/users/{session["user_id"]}')
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
            return redirect(f'/users/{session["user_id"]}')
        else:
            #Not sure why we had to clear the session within the view function rather than in tests.
            #Maybe the session in the view function itself and the session in the test client are two
            #different entities?
            session.clear()
            form.username.errors.append("Incorrect username/password combination.")
    return render_template('login.html', form=form)

@app.route('/users/<username>')
def show_user_details(username):
    """A view function that is dependent on a user being logged in. If a user is logged in, it renders
    'userdetails.html' with user details for the user with the id in the url. If a user is not logged in,
    it returns a redirect to '/login' with the flashed message 'Please log in to access this page.'"""
    if session.get("user_id") != None:
        user = User.query.get(username)
        return render_template('userdetails.html', user=user)
    else:
        flash("Please log in to access this page.")
        return redirect('/login')


@app.route('/logout')
def logout_user():
    """A view function that clears any data from the session, logging any current user out, then
    flashes a message declaring success and returns a redirect to '/', eventually rendering 'register.html'"""
    session.clear()
    flash("Successfully logged out.")
    return redirect('/')