from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from datetime import datetime


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User')  # Odstranjen backref 'notes'


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    notes = db.relationship('Note')
    banned = db.Column(db.Boolean, default=False)
    

class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team_name = db.Column(db.String(100), nullable=False)
    match_date = db.Column(db.DateTime, nullable=False)
    person_name = db.Column(db.String(100), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    day = db.Column(db.Integer, nullable=False) 


class Message(db.Model):
    __tablename__ = 'messages'  # ← Točno tako kot v schema.sql
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    subject = db.Column(db.String(255))
    message = db.Column(db.Text, nullable=False)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)



class Registration(db.Model):
    __tablename__ = "registrations"  
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    full_name = db.Column(db.String(255), nullable=False)
    age = db.Column(db.Integer)
    position = db.Column(db.String(100))
    team_name = db.Column(db.String(255))
    phone_number = db.Column(db.String(20))
    paid = db.Column(db.Boolean, default=False)
    registration_date = db.Column(db.DateTime(timezone=True), server_default=func.now())


