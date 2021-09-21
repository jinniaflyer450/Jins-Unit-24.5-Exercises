from flask import Flask, render_template, redirect, flash, session
from flask_sqlalchemy import SQLAlchemy
from models import User
from forms import RegisterForm, LoginForm
import requests
from sqlalchemy.exc import IntegrityError
from unittest import TestCase

app.config['SECRET_KEY'] = 'catdog'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Ob1wankenobi@localhost/auth_practice_tests'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

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

    def test_register_user_get(self):
        with app.test_client() as client:
            request = client.get('/register')
            self.assertEqual(request.status_code, 200)
            response = request.get_data(as_text=True)
            self.assertIn('<h1>Register</h1>', response)
            self.assertIn('<button>Register</button>', response)