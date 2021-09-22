"""The test file for the Commentator app."""

from flask import Flask, render_template, redirect, flash, session
from flask_sqlalchemy import SQLAlchemy
from models import User, db, connect_db
from forms import RegisterForm, LoginForm
import requests
from sqlalchemy.exc import IntegrityError
from unittest import TestCase
from app import app

app.config['SECRET_KEY'] = 'catdog'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Ob1wankenobi@localhost/auth_practice_tests'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['WTF_CSRF_ENABLED'] = False
app.config['TESTING']=True

#The dummy user used for most of the tests.
d={'username': 'newuser1', 'password': 'password123', 'email': 'email@email.com',
            'first_name': 'John', 'last_name': 'Doe'}

class AuthAppTests(TestCase):
    """A series of tests for the Commentator app."""
    @classmethod
    def setUpCls(cls):
        """Readies database tables for the first test."""
        db.create_all()
        db.session.commit()

    def setUp(self):
        """Resets the database before each test."""
        db.drop_all()
        db.session.commit()
        db.create_all()
        db.session.commit()

    def tearDown(self):
        """Resets the database after each test."""
        db.drop_all()
        db.session.commit()

    def test_register_method(self):
        """Tests to confirm that the register method on the User model returns a user with
        the appropriate properties."""
        with app.test_client() as client:
            user = User.register(d["username"], d["password"], d["email"], d["first_name"], d["last_name"])
            self.assertEqual(user.username, 'newuser1')
            self.assertNotEqual(user.password, 'password123')
            self.assertEqual(user.email, 'email@email.com')
            self.assertEqual(user.first_name, 'John')
            self.assertEqual(user.last_name, 'Doe')

    def test_register_user_get(self):
        """Tests to confirm that the view function 'register_user' returns 'register.html' on a 
        GET request to '/register'.'"""
        with app.test_client() as client:
            request = client.get('/register')
            self.assertEqual(request.status_code, 200)
            response = request.get_data(as_text=True)
            self.assertIn('<h1>Register</h1>', response)
            self.assertIn('<button>Register</button>', response)
    
    def test_register_user_successful(self):
        """Tests to confirm that the view function 'register_user' successfully registers an instance
        of the User model in the database on a POST request to '/register' given information that passes 
        validation, stores the user's username in the session, and returns a redirect to '/secret'."""
        with app.test_client() as client:
            request = client.post('/register', data=d, follow_redirects=True)
            self.assertEqual(request.status_code, 200)
            response = request.get_data(as_text=True)
            self.assertIn("You made it!", response)
            self.assertEqual(User.query.count(), 1)
            self.assertEqual(session["user_id"], 
            User.query.filter_by(username='newuser1').first().username)
    
    def test_register_user_duplicate_username(self):
        with app.test_client() as client:
            """Tests to confirm that if the view function 'register_user' receives a registration
            attempt that contains a username that is a duplicate of an existing user's username on a 
            POST request to '/register', it does not add the new attempt to the database and renders 
            'register.html' again with the 'duplicate username' error on the page."""
            client.post('/register', data=d, follow_redirects=True)
            request=client.post('/register', data=d, follow_redirects=True)
            self.assertEqual(request.status_code, 200)
            response = request.get_data(as_text=True)
            self.assertIn("<title>Register</title>", response)
            self.assertIn("Username already taken. Please choose another.", response)
            self.assertEqual(User.query.count(), 1)
    
    def test_register_user_missing_info(self):
        """Tests to confirm that if the view function 'register_user' receives a registration
        attempt that does not contain required data on a POST request to '/register', it does
        not add the new attempt to the database and renders 'register.html' again with one of the
        'missing data' errors on the page."""
        with app.test_client() as client:
            missing_data={'username': 'newuser1', 'password': 'password123', 'email': 'email@email.com',
            'first_name': 'John', 'last_name': ''}
            request=client.post('/register', data=missing_data, follow_redirects=True)
            self.assertEqual(request.status_code, 200)
            response = request.get_data(as_text=True)
            self.assertIn("<title>Register</title>", response)
            self.assertIn("Last name required.", response)
            self.assertEqual(User.query.count(), 0)

    def test_authenticate_method(self):
        """Tests to confirm that the authenticate method on the User model returns a user from the
        database if given the correct username and password for that user and that it returns False
        if the username-password combination does not match an existing user."""
        with app.test_client() as client:
            client.post('/register', data=d, follow_redirects=True)
            user_in_db = User.query.filter_by(username='newuser1').first()
            self.assertEqual(user_in_db, User.authenticate('newuser1', 'password123'))
            self.assertFalse(User.authenticate('newuser1', 'incorrectpassword'))
            self.assertFalse(User.authenticate('newuser2', 'password123'))
    
    def test_login_user_get(self):
        """Tests to confirm that the view function 'login_user' returns 'login.html' on a GET
        request to '/login'."""
        with app.test_client() as client:
            request=client.get('/login')
            response=request.get_data(as_text=True)
            self.assertIn("<title>Log In</title>", response)
            self.assertIn("<button>Log In</button>", response)
    
    def test_login_user_successful(self):
        """Tests to confirm that the view function 'login_user' successfully stores a user's username
        in session (returns a redirect to '/secret') and returns 'You made it!' on a POST request to 
        '/login' if the POST request contains a username and password that matches a user in the 
        database."""
        with app.test_client() as client:
            client.post('/register', data=d, follow_redirects=True)
            session.pop("user_id")
            self.assertIsNone(session.get("user_id"))
            request = client.post('/login', data={"username":d["username"], "password":d["password"]}, 
            follow_redirects=True)
            self.assertEqual(request.status_code, 200)
            response = request.get_data(as_text=True)
            self.assertIn("You made it!", response)
            self.assertEqual(session["user_id"], 'newuser1')
    
    def test_login_user_wrong_username(self):
        """Tests to confirm that the view function 'login_user' renders 'login.html' with a 
        'username/password combination is incorrect' error on a POST request to '/login' if
        a user attempts to log in with a username that does not match any user in the 
        database, even if the password is the same as an existing user's. No username
        should be stored in session."""
        with app.test_client() as client:
            client.post('/register', data=d, follow_redirects=True)
            session.clear()
            self.assertIsNone(session.get("user_id"))
            request=client.post('/login', data={"username": 'newuser2', "password": d["password"]},
            follow_redirects=True)
            self.assertEqual(request.status_code, 200)
            response=request.get_data(as_text=True)
            self.assertIn("<title>Log In</title>", response)
            self.assertIn("Incorrect username/password combination.", response)
            self.assertIsNone(session.get("user_id"))
    
    def test_login_user_wrong_password(self):
        """Tests to confirm that the view function 'login_user' renders 'login.html' with a 
        'username/password combination is incorrect' error on a POST request to '/login' if
        a user attempts to log in with a username that matches a user in the database but a 
        password that does not match the user's password when its hash is compared to the user's
        stored hash. No username should be stored in session."""
        with app.test_client() as client:
            client.post('/register', data=d, follow_redirects=True)
            session.clear()
            self.assertIsNone(session.get("user_id"))
            request=client.post('/login', data={"username": d["username"], "password": "wrongpassword"},
            follow_redirects=True)
            self.assertEqual(request.status_code, 200)
            response=request.get_data(as_text=True)
            self.assertIn("<title>Log In</title>", response)
            self.assertIn("Incorrect username/password combination.", response)
            self.assertIsNone(session.get("user_id"))
    
    def test_secret_route(self):
        """Tests to confirm that the view function 'secret_route' renders 'You made it!' on a GET request
        to '/secret'."""
        with app.test_client() as client:
            request = client.get('/secret', follow_redirects=True)
            self.assertEqual(request.status_code, 200)
            response = request.get_data(as_text=True)
            self.assertIn("You made it!", response)
    
    def test_logout_user(self):
        """Tests to confirm that the view function 'logout_user' returns a redirect to '/' (eventually
        rendering 'register.html') with the flashed message 'Succesfully logged out.'. There should
        be no information in the session afterward, even if there would have been before the request."""
        with app.test_client() as client:
            client.post('/register', data=d, follow_redirects=True)
            self.assertEqual(session.get("user_id"), "newuser1")
            request = client.get('/logout', follow_redirects=True)
            self.assertEqual(request.status_code, 200)
            response = request.get_data(as_text=True)
            self.assertIn("Successfully logged out.", response)
            self.assertIn("<title>Register</title>", response)
            self.assertIsNone(session.get("user_id"))

