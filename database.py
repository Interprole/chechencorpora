from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager

db = SQLAlchemy()
login_manager = LoginManager()


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    login = db.Column(db.String(80), primary_key=True, nullable=False)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)


class Corpus(db.Model):
    __tablename__ = 'corpora'
    name = db.Column(db.String(80), primary_key=True)
    source = db.Column(db.String(150))
    diolect = db.Column(db.String(150), db.ForeignKey('diolects.name'))
    description = db.Column(db.Text())


class Diolect(db.Model):
    __tablename__ = 'diolects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)


def init_database(app):
    db.init_app(app)


def init_login_manager(app):
    login_manager.init_app(app)


@login_manager.user_loader
def load_user(login):
    return User.query.filter(
        (User.login == login) | (User.email == login)
        ).first()


def create_database():
    db.create_all()


def add_corpus(name, source, diolect, description):
    corpus = Corpus(name, source, diolect, description)
    db.session.add(corpus)
    db.commit()


def add_user(login, name, email, password):
    user = User(login, name, email, password)
    db.session.add(user)
    db.commt()


def retrieve_corpora():
    return Corpus.query.all()

