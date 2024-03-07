from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)


class Corpora(db.Model):
    __tablename__ = 'corpora'
    id = db.Column(db.Integer, primary_key=True)
    diolect = db.Column(db.String(150), unique=True,
                        db.ForeignKey('diolects.name'))


class Diolects(db.Model):
    __tablename__ = 'diolects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)


def get_corps():
    return db.session.query(Corpora).all()


