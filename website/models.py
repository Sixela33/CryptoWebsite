from datetime import timezone
from enum import unique
from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class Codes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(1000))
    link = db.Column(db.String(10000))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(1500))
    userName = db.Column(db.String(150))
