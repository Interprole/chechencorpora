from flask import Flask, render_template, request, redirect, Response, session
import os
from database import retrieve_corpora, init_database, create_database
from dotenv import load_dotenv

app = Flask(__name__)

# env from .env file
load_dotenv()

# env variables
DATABASE_HOST = os.getenv("POSTGRES_HOST")
DATABASE_NAME = os.getenv("POSTGRES_DATABASE")
DATABASE_USER = os.getenv("POSTGRES_USER")
DATABASE_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DATABASE_URL = f"postgresql+psycopg2://{DATABASE_USER}:{DATABASE_PASSWORD}"\
                f"@{DATABASE_HOST}/{DATABASE_NAME}"\
                f"?sslmode=require"

# initializing app
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
init_database(app)
with app.app_context():
    create_database()


@app.route('/')
def base():
    return render_template('base.html')


@app.route('/corpora')
def corpora():
    corps = retrieve_corpora()
    return render_template('corpora.html', corps=corps)


if __name__ == '__main__':
    app.run(port=80, debug=True)
