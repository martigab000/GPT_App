from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    payer_id = db.Column(db.String(10000))
    payer_name = db.Column(db.String(10000))
    payer_info = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    notes = db.relationship('Note')
    inputs = db.relationship('Input')


class Input(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    responses = db.relationship('Response')
    

class Response(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    input_id = db.Column(db.Integer, db.ForeignKey('input.id'))
    

class Payer(db.Model):
    __tablename__ = 'payer'
    id = db.Column(db.Integer, primary_key=True)
    payer_name = db.Column(db.String(50), nullable=False)
    payer_ids = db.relationship('PayerID', backref='payer', lazy=True)
    c_house_id = db.Column(db.Integer, db.ForeignKey('chouse.id'))

class PayerID(db.Model):
    __tablename__ = 'payer_id'
    id = db.Column(db.Integer, primary_key=True)
    payer_id = db.Column(db.String(10), nullable=False)
    payer_name_id = db.Column(db.Integer, db.ForeignKey('payer.id'), nullable=False)

class Chouse(db.Model):
    __tablename__ = 'chouse'
    id = db.Column(db.Integer, primary_key=True)
    c_name = db.Column(db.String(50), unique=True, nullable=False)
    payers = db.relationship('Payer', backref='c_house', lazy=True)

    