from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager
from sqlalchemy.orm import selectinload
import random
import re

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


class Sentence(db.Model):
    __tablename__ = 'sentences'
    id = db.Column(db.Integer, primary_key=True)
    corpus_id = db.Column(db.Integer, db.ForeignKey('corpora.id'),
                          nullable=False)
    text = db.Column(db.String(1000), nullable=False)
    translation = db.Column(db.String(1000), nullable=True)
    corpus = db.relationship('Corpus', backref='sentences', lazy=True)

    def tokenize(self):
        # Регулярное выражение для токенизации по пробелам и любым символам, кроме знаков препинания
        pattern = r'\w+'

        # Применяем регулярное выражение к тексту
        tokens = re.findall(pattern, self.text)
        return enumerate(tokens)

    def word(self, word_id):
        word = [word for i, word in self.tokenize() if i == word_id]
        return word[0]


# Ассоциативная таблица для связи многие-ко-многим между Morph и Gloss
morph_gloss_association = db.Table(
    'morph_gloss_association',
    db.Column('morph_id', db.Integer, db.ForeignKey('morphs.id')),
    db.Column('gloss_id', db.Integer, db.ForeignKey('glosses.id'))
)

# Ассоциативная таблица для связи многие-ко-многим между Segment и Gloss
word_morph_association = db.Table(
    'word_morph_association',
    db.Column('word_id', db.Integer, db.ForeignKey('words.id')),
    db.Column('morph_id', db.Integer, db.ForeignKey('morphs.id'))
)


class Word(db.Model):
    __tablename__ = 'words'
    id = db.Column(db.Integer, primary_key=True)
    sentence_id = db.Column(db.Integer, db.ForeignKey('sentences.id'))
    number = db.Column(db.Integer, nullable=False)
    sentence = db.relationship('Sentence', backref='words', lazy=True)

    morphs = db.relationship('Morph', secondary=word_morph_association,
                             backref='words', lazy='select')


class Gloss(db.Model):
    __tablename__ = 'glosses'
    id = db.Column(db.Integer, primary_key=True)
    gloss = db.Column(db.String(100), unique=True)
    definition = db.Column(db.String(200), nullable=False)
    note = db.Column(db.Text(), nullable=True)


class Morph(db.Model):
    __tablename__ = 'morphs'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(200), nullable=False)
    idiom_id = db.Column(db.Integer, db.ForeignKey('idioms.id'),
                         nullable=False)
    idiom = db.relationship('Idiom', backref='morphs', lazy=True)
    # Связь многие-ко-многим с таблицей Gloss через ассоциативную таблицу
    glosses = db.relationship('Gloss', secondary=morph_gloss_association,
                              backref='morphs', lazy=True)


"""class Segment(db.Model):
    __tablename__ = 'segms'
    id = db.Column(db.Integer, primary_key=True)
    word_id = db.Column(db.Integer, db.ForeignKey('words.id'),
                        nullable=False)
    morph_id = db.Column(db.Integer, db.ForeignKey('morphs.id'),
                         nullable=False)
    number = db.Column(db.Integer, nullable=False)

    morph = db.relationship('Morph', lazy=True)
    word = db.relationship('Word', backref='segms', lazy='select')

    # Связь многие-ко-многим с таблицей Gloss через ассоциативную таблицу
    glosses = db.relationship('Gloss', secondary=segm_gloss_association,
                              backref='segms', lazy='select')"""


class Idiom(db.Model):
    __tablename__ = 'idioms'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('idioms.id'), nullable=True)
    group = db.relationship('Idiom', remote_side=[id])
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
    db.session.commit


def add_gloss(gloss, definition, note):
    gloss = Gloss(id=random.randint(0, 99999999),
                  gloss=gloss,
                  definition=definition,
                  note=note
                  )
    db.session.add(gloss)
    db.session.commit()


def add_sentence(corpus_id, text, translation):
    sentence = Sentence(id=random.randint(0, 99999999),
                        corpus_id=corpus_id,
                        text=text,
                        translation=translation)
    db.session.add(sentence)
    db.session.commit()


def add_word(sentence_id, morphs, number):
    word = Word.query.filter_by(sentence_id=sentence_id,
                                number=number).first()

    # Обновляем его свойства
    if word:
        word.morphs = morphs
        db.session.commit()
    else:
        word = Word(id=random.randint(0, 99999999),
                    sentence_id=sentence_id,
                    number=number)
        word.morphs = morphs
        db.session.add(word)
        db.session.commit()


"""def add_segment(word_id, morph_id, number):
    segment = Segment(id=random.randint(0, 99999999),
                      word_id=word_id,
                      morph_id=morph_id,
                      number=number)
    db.session.add(segment)
    db.session.commit()"""


def add_morph(text, glosses, idiom_id):
    morph = Morph(id=random.randint(0, 99999999),
                  text=text,
                  idiom_id=idiom_id)
    morph.glosses = glosses
    db.session.add(morph)
    db.session.commit()


def search_morph(text):
    query = (
        db.session.query(Word)
        .join(Word.morphs)
        .options(selectinload(Word.morphs))
        .filter(Morph.text == text)
        )

    words = query.all()
    return words


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


def get_glosses(gloss=None, id=None, ids=[]):
    if gloss:
        return Gloss.query.filter(Gloss.gloss == gloss).first()
    if id:
        return Gloss.query.get(id)
    if ids:
        return Gloss.query.filter(Gloss.id.in_(ids)).all()
    return Gloss.query.all()


def get_words():
    return Word.query.all()


def get_morphs(text=None, id=None, idiom_id=None, glosses=[],
               ids=[]):
    if text and idiom_id and glosses:
        query = db.session.query(Morph)
        query = query.filter(Morph.text == text,
                             Morph.idiom_id == idiom_id)
        for gloss in glosses:
            query = query.filter(Morph.glosses.contains(gloss))
        return query.first()
    if text:
        return Morph.query.filter(Morph.text == text).first()
    if id:
        return Morph.query.get(id)
    if ids:
        return Morph.query.filter(Morph.id.in_(ids)).all()
    return Morph.query.all()


def get_idioms(name=None, id=None):
    if name:
        return Idiom.query.filter(Idiom.name == name).first()
    if id:
        return Idiom.query.get(id)
    return Idiom.query.all()
