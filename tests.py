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
app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['WTF_CSRF_ENABLED'] = False

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
            d = {'username': 'newuser1', 'password': 'password123', 'email': 'email@email.com',
            'first_name': 'John', 'last_name': 'Doe'}
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
            d = {'username': 'newuser1', 'password': 'password123', 'email': 'email@email.com',
            'first_name': 'John', 'last_name': 'Doe'}
            request = client.post('/register', data=d, follow_redirects=True)
            self.assertEqual(request.status_code, 200)
            response = request.get_data(as_text=True)
            self.assertIn("You made it!", response)
            self.assertEqual(User.query.count(), 1)
            self.assertEqual(session["user_id"], 
            User.query.filter_by(username='newuser1').first().username)
    
    def test_register_user_duplicate_username(self):
        with app.test_client() as client:
            d = {'username': 'newuser1', 'password': 'password123', 'email': 'email@email.com',
            'first_name': 'John', 'last_name': 'Doe'}
            client.post('/register', data=d, follow_redirects=True)
            request=client.post('/register', data=d, follow_redirects=True)
            self.assertEqual(request.status_code, 200)
            response = request.get_data(as_text=True)
            self.assertIn("<title>Register</title>", response)
            self.assertIn("Username already taken. Please choose another.", response)
            self.assertEqual(User.query.count(), 1)
    
    def test_register_user_missing_info(self):
        with app.test_client() as client:
            d={'username': 'newuser1', 'password': 'password123', 'email': 'email@email.com',
            'first_name': 'John', 'last_name': ''}
            request=client.post('/register', data=d, follow_redirects=True)
            self.assertEqual(request.status_code, 200)
            response = request.get_data(as_text=True)
            self.assertIn("<title>Register</title>", response)
            self.assertIn("Last name required.", response)