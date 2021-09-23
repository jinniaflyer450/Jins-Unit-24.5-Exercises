from flask import Flask
from flask_bcrypt import Bcrypt
from models import db, connect_db, User

bcrypt=Bcrypt()

def seed_users():
    new_user = User.register(username='newuser1', password='password123', email='email@email.com',
    first_name='John', last_name='Doe')
    new_user_2 = User.register(username='newuser2', password='password456', email='email2@email.com',
    first_name='Jane', last_name='Doe')
    new_user_3 = User.register(username='newuser3', password='password789', email='email3@email.com',
    first_name='Joe', last_name='Doe')

    db.session.add_all([new_user, new_user_2, new_user_3])
    db.session.commit()
