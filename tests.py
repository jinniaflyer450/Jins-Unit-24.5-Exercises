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


d={'username': 'newuser1', 'password': 'password123', 'email': 'email@email.com',
            'first_name': 'John', 'last_name': 'Doe'}

class AuthAppTests(TestCase):
    @classmethod
    def setUpCls(cls):
        db.create_all()
        db.session.commit()

    def setUp(self):
        db.drop_all()
        db.session.commit()
        db.create_all()
        db.session.commit()

    def tearDown(self):
        db.drop_all()
        db.session.commit()

    def test_register_method(self):
        with app.test_client() as client:
            user = User.register(d["username"], d["password"], d["email"], d["first_name"], d["last_name"])
            self.assertEqual(user.username, 'newuser1')
            self.assertNotEqual(user.password, 'password123')
            self.assertEqual(user.email, 'email@email.com')
            self.assertEqual(user.first_name, 'John')
            self.assertEqual(user.last_name, 'Doe')

    def test_register_user_get(self):
        with app.test_client() as client:
            request = client.get('/register')
            self.assertEqual(request.status_code, 200)
            response = request.get_data(as_text=True)
            self.assertIn('<h1>Register</h1>', response)
            self.assertIn('<button>Register</button>', response)
    
    def test_register_user_successful(self):
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
            client.post('/register', data=d, follow_redirects=True)
            request=client.post('/register', data=d, follow_redirects=True)
            self.assertEqual(request.status_code, 200)
            response = request.get_data(as_text=True)
            self.assertIn("<title>Register</title>", response)
            self.assertIn("Username already taken. Please choose another.", response)
            self.assertEqual(User.query.count(), 1)
    
    def test_register_user_missing_info(self):
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
        with app.test_client() as client:
            client.post('/register', data=d, follow_redirects=True)
            user_in_db = User.query.filter_by(username='newuser1').first()
            self.assertEqual(user_in_db, User.authenticate('newuser1', 'password123'))
            self.assertFalse(User.authenticate('newuser1', 'incorrectpassword'))
            self.assertFalse(User.authenticate('newuser2', 'password123'))
    
    def test_login_user_get(self):
        with app.test_client() as client:
            request=client.get('/login')
            response=request.get_data(as_text=True)
            self.assertIn("<title>Log In</title>", response)
            self.assertIn("<button>Log In</button>", response)
    
    def test_login_user_successful(self):
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