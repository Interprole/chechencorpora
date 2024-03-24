from sklearn.neighbors import KNeighborsClassifier
import random
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
    init_login_manager,
    find_user
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

HOST = os.getenv("HOST")
PORT = os.getenv("PORT")

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
        rand_id = random.randint(0, 99999999)

        # Validating login and password
        if find_user(login):
            return render_template('signup.html', error='existing login')
        if find_user(email):
            return render_template('signup.html', error='existing email')

        # Hash password
        hashed_password = bcrypt.generate_password_hash(
            password
                ).decode("utf-8")

        # Create and save new user
        add_user(id=rand_id,
                 login=login,
                 name=name,
                 email=email,
                 password=hashed_password)

        # Success message and redirection
        return redirect(url_for('login'))

    return render_template('signup.html')


@app.route('/my_corpora')
def my_corpora():
    return render_template('corpora.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/account')
def account():
    return render_template('account.html')


@app.route('/signin', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('signin.html')

    login = request.form.get('login')
    password = request.form.get('password')
    remember = request.form.get('remember') == 'on'

    user = find_user(login)

    # Validate credentials
    if user:
        if bcrypt.check_password_hash(user.password, password):
            # Successful login
            login_user(user, remember=remember)

            return redirect(url_for('home'))

        error = 'wrong password'
    else:
        error = 'invalid login'

    # Failed login
    return render_template('signin.html', error=error)


if __name__ == '__main__':
    app.run(host=HOST, port=PORT, debug=True)
