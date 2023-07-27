import sqlalchemy as db
from core.db import Base


class Users(Base):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(255), unique=True, nullable=False)
    registration_date = db.Column(db.Date, nullable=False)


class Credits(Base):
    __tablename__ = 'credits'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    issuance_date = db.Column(db.Date, nullable=False)
    return_date = db.Column(db.Date, nullable=False)
    actual_return_date = db.Column(db.Date, nullable=True)
    body = db.Column(db.Integer, nullable=False)
    percent = db.Column(db.types.Numeric(precision=10, scale=2), nullable=False)


class Dictionary(Base):
    __tablename__ = 'dictionary'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)


class Payments(Base):
    __tablename__ = 'payments'
    id = db.Column(db.Integer, primary_key=True)
    credit_id = db.Column(db.Integer, db.ForeignKey('credits.id'), nullable=False)
    payment_date = db.Column(db.Date, nullable=False)
    type_id = db.Column(db.Integer, db.ForeignKey('dictionary.id'), nullable=False)
    sum = db.Column(db.types.Numeric(precision=10, scale=2), nullable=False)


class Plans(Base):
    __tablename__ = 'plans'
    id = db.Column(db.Integer, primary_key=True)
    period = db.Column(db.Date, nullable=False)
    sum = db.Column(db.Integer, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('dictionary.id'), nullable=False)
