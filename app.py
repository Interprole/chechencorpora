from flask import (
    Flask,
    render_template,
    request,
    redirect,
    Response,
    url_for
    )
from flask_login import (
    login_user,
    login_required,
    current_user,
    logout_user
    )
from flask_bcrypt import Bcrypt
import os
from database import (
    retrieve_corpora,
    init_database,
    create_database,
    add_user,
    add_corpus,
    load_user,
    init_login_manager
    )
from dotenv import load_dotenv

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

SECRET_KEY = os.getenv('SECRET_KEY')

# Initializing app
app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
bcrypt = Bcrypt(app)

# Initializing database
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
init_database(app)
with app.app_context():
    create_database()
init_login_manager(app)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/corpora')
def corpora():
    corpora = retrieve_corpora()
    return render_template('corpora.html', corpora=corpora)


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        login = request.form['login']
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        # Validating login and password
        if load_user(login):
            return render_template('signup.html', error='existing login')
        if load_user(email):
            return render_template('signup.html', error='existing email')

        # Hash password
        hashed_password = bcrypt.generate_password_hash(
            password._unicode_to_bytes()
            )

        # Create and save new user
        add_user(login=login,
                 name=name,
                 email=email,
                 password=hashed_password)

        # Success message and redirection
        return redirect(url_for('login'))

    return render_template('signup.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()


@app.route('/signin', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('signin.html')

    login = request.form['login']
    password = request.form['password']

    user = load_user(login)

    # Validate credentials
    if user:
        if bcrypt.check_password_hash(user.password,
                                      password._unicode_to_bytes()):
            # Successful login
            login_user(user)
            return redirect(url_for('home'))

        error = 'imvalid login'
    error = 'wrong password'

    # Failed login
    return render_template('signin.html', error=error)


if __name__ == '__main__':
    app.run(port=80, debug=True)
