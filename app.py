from flask import Flask, render_template, request, redirect, Response, session
from database import *
import os

app = Flask(__name__)
DATABASE_HOST = os.getenv("DATABASE_HOST")
DATABASE_NAME = os.getenv("DATABASE_NAME")
DATABASE_USER = os.getenv("DATABASE_USER")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")

DATABASE_URL = f"postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}"\
                    f"@{DATABASE_HOST}{DATABASE_NAME}"

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
db.init_app(app)


@app.route('/')
def base():
    return render_template('base.html')


@app.route('/corpora')
def corpora():
    return render_template('corpora.html', corps=get_corps())


if __name__ == '__main__':
    app.run(port=80, debug=False)
