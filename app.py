from flask import Flask, render_template, request, redirect, Response, session
from database import *
import os

app = Flask(__name__)
psql_url = os.getenv("POSTGRES_URL_NON_POOLING")
app.config['SQLALCHEMY_DATABASE_URI'] = psql_url
db.init_app(app)


@app.route('/')
def base():
    return render_template('base.html')


@app.route('/corpora')
def corpora():
    return render_template('corpora.html', corps=get_corps())


if __name__ == '__main__':
    app.run(port=80, debug=False)
