from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager
import random

db = SQLAlchemy()
login_manager = LoginManager()


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    login = db.Column(db.String(80), nullable=False, unique=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(500), nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)


class Corpus(db.Model):
    __tablename__ = 'corpora'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    source = db.Column(db.String(150))
    idiom_id = db.Column(db.Integer, db.ForeignKey('idioms.id'),
                         nullable=False)
    description = db.Column(db.Text())


class Idiom(db.Model):
    __tablename__ = 'idioms'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('idioms.id'), nullable=True)
    group = db.relationship("Idiom", remote_side=[id])
    corpora = db.relationship('Corpus', backref='idiom', lazy=True)


def init_database(app):
    db.init_app(app)


def init_login_manager(app):
    login_manager.init_app(app)


def find_user(login):
    return User.query.filter(
        (User.login == login) | (User.email == login)
        ).first()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def create_database():
    db.create_all()


def add_corpus(name, source, idiom_id, description):
    corpus = Corpus(id=random.randint(0, 99999999),
                    name=name,
                    source=source,
                    idiom_id=idiom_id,
                    description=description
                    )
    db.session.add(corpus)
    db.session.commit()


def add_user(login, name, email, password):
    user = User(id=random.randint(0, 99999999),
                login=login,
                name=name,
                email=email,
                password=password)
    db.session.add(user)
    db.session.commit()


def add_idiom(name, group_id=None):
    id = random.randint(0, 99999999)
    idiom = Idiom(id=id,
                  name=name,
                  group_id=group_id)
    db.session.add(idiom)
    db.session.commit()


def get_corpora(name=None, id=None):
    if name:
        return Corpus.query.filter(Corpus.name == name).first()
    if id:
        return Corpus.query.get(id)
    return Corpus.query.all()


def get_idioms(name=None, id=None):
    if name:
        return Idiom.query.filter(Idiom.name == name).first()
    if id:
        return Idiom.query.get(id)
    return Idiom.query.all()
