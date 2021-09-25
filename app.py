"""Commentator: An app where users can register, log in to their accounts, and log out. 
While they are logged in, they can submit, edit, and delete feedback, 
as well as updating or deleting their own accounts."""

from flask import Flask, render_template, redirect, flash, session
from flask_sqlalchemy import SQLAlchemy
from models import db, connect_db, User, Feedback
from forms import RegisterForm, LoginForm, FeedbackForm
import requests
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config['SECRET_KEY'] = 'catdog'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Ob1wankenobi@localhost/auth_practice'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['WTF_CSRF_ENABLED'] = False

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
        return redirect(f'/users/{new_user.username}')
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
            return redirect(f'/users/{user.username}')
        else:
            #Not sure why we had to clear the session within the view function rather than in tests.
            #Maybe the session in the view function itself and the session in the test client are two
            #different entities?
            session.clear()
            form.username.errors.append("Incorrect username/password combination.")
    return render_template('login.html', form=form)

@app.route('/users/<username>')
def show_user_details(username):
    """A view function that shows 'userdetails.html' with user details (username, name, and password) for 
    the user in the URL if a user is logged in. If no user is logged in, it returns a redirect to '/login'
    with the flashed message 'Please log in to view this page.'"""
    if session.get("user_id"):
        user = User.query.get_or_404(username)
        feedback = Feedback.query.filter_by(username=username).all()
        return render_template('userdetails.html', user=user, feedback=feedback)
    else:
        flash("Please log in to view this page.")
        return redirect('/login')

@app.route('/users/<username>/delete', methods=["POST"])
def delete_user(username):
    """A view function that allows a logged-in user to delete their account, removing it and all
    its feedback from the database and redirecting to '/'."""
    user = User.query.get_or_404(username)
    if session.get("user_id") != username:
        flash("You do not have permission to delete this user.")
        return redirect(f'/users/{username}')
    else:
        db.session.delete(user)
        db.session.commit()
        flash(f"Successfully deleted the user {username}!")
        return redirect('/')

@app.route('/logout')
def logout_user():
    session.clear()
    flash("Successfully logged out.")
    return redirect('/')

@app.route('/feedback/<int:feedback_id>/update', methods=["GET", "POST"])
def show_edit_feedback(feedback_id):
    """A view function that shows 'editfeedback.html'. If no user or a user who did not create the post is 
    logged in, they see the title, user, and content of the feedback. If the user who created the post is
    logged in, they see the above plus a form to edit the post."""
    feedback = Feedback.query.get_or_404(feedback_id)
    form = FeedbackForm(obj={"title": feedback.title, "content": feedback.content})
    if form.validate_on_submit():
        if session.get("user_id") != feedback.username:
            flash("You do not have permission to edit this feedback.")
            return render_template('editfeedback.html', feedback=feedback, form=form)
        feedback.title = form.title.data
        feedback.content = form.content.data
        db.session.commit()
        flash("Feedback successfully edited!")
        return render_template('editfeedback.html', feedback=feedback, form=form)
    return render_template('editfeedback.html', feedback=feedback, form=form)

@app.route('/feedback/<int:feedback_id>/delete', methods=["POST"])
def delete_feedback(feedback_id):
    """A view function that redirects to '/users/username' after deleting the piece of feedback noted in the
    URL from the database if and only if the user who created the feedback is logged in."""
    feedback = Feedback.query.get_or_404(feedback_id)
    if session.get("user_id") != feedback.username:
        flash("You do not have permission to delete this feedback.")
        return redirect(f'/feedback/{feedback_id}/update')
    db.session.delete(feedback)
    db.session.commit()
    flash("Successfully deleted feedback!")
    return redirect(f'/users/{session.get("user_id")}')

@app.route('/users/<username>/feedback/add', methods=["GET", "POST"])
def add_feedback(username):
    """A view function that on a GET request returns 'addfeedback.html' with a form to add new
    feedback if and only if the current user matches the user in the URL. On a POST request, if the 
    form validates correctly, it adds a new piece of feedback written by the current user to the database 
    if and only if the current user matches the user in the URL."""
    if session.get("user_id") != username:
        flash("You do not have permission to add feedback for this user.")
        return redirect(f'/users/{username}')
    else:
        form = FeedbackForm()
        if form.validate_on_submit():
            feedback = Feedback(title=form.title.data, content=form.content.data, username=username)
            db.session.add(feedback)
            db.session.commit()
            flash("Successfully added feedback!")
            return redirect(f'/feedback/{feedback.id}/update')
        return render_template('addfeedback.html', form=form, username=username)