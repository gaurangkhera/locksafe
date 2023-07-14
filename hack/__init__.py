import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import stripe

# app & extensions config
app =  Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

app.config['SECRET_KEY'] = 'secret'
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.path.join(basedir,'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['STRIPE_PUBLIC_KEY'] = 'pk_test_51NTgT6SAvDl2UTdKhZ5BOMiSCEJ5zQ8Gd0aiOcjIqWAG8wiMHOoSgW1U0ykaPgob27lDECWRW7H6GW9JacjjmSsJ00Iy6SDvkv'
app.config['STRIPE_SECRET_KEY'] = 'sk_test_51NTgT6SAvDl2UTdKQM3LUyirhm3n4DQbWtLhY8b4QX6vajOaBgFcNP2TGMLcvjyu1RSH7Z3NR7T1k7GTucNe52aN0069n7nZh2'
db = SQLAlchemy(app)
Migrate(app,db)

def create_db(app):
    with app.app_context():
        db.create_all()