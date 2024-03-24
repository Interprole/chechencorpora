from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager

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
    name = db.Column(db.String(80), primary_key=True)
    source = db.Column(db.String(150))
    dialect = db.Column(db.String(150), db.ForeignKey('dialects.name'))
    description = db.Column(db.Text())


class Dialect(db.Model):
    __tablename__ = 'dialects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)


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


def add_corpus(name, source, dialect, description):
    corpus = Corpus(name=name,
                    source=source,
                    dialect=dialect,
                    description=description
                    )
    db.session.add(corpus)
    db.session.commit()


def add_user(id, login, name, email, password):
    user = User(id=id,
                login=login,
                name=name,
                email=email,
                password=password)
    db.session.add(user)
    db.session.commit()


def retrieve_corpora():
    return Corpus.query.all()
