from sklearn.neighbors import KNeighborsClassifier
import plotly.graph_objects as go
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
    get_corpora,
    init_database,
    create_database,
    add_user,
    add_corpus,
    load_user,
    init_login_manager,
    find_user,
    get_idioms,
    add_idiom
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


@app.route('/corpora', methods=['POST', 'GET'])
def corpora():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        source = request.form.get('source')
        idiom_id = get_idioms(
            request.form.get('idiom')).id

        if get_corpora(name=name):
            message = 'existing corpus'
        else:
            add_corpus(name=name,
                       source=source,
                       description=description,
                       idiom_id=idiom_id)
            message = 'success'

    corpora = get_corpora()
    idioms = get_idioms()
    message = ''

    return render_template('corpora.html', corpora=corpora,
                           message=message, idioms=idioms)


@app.route('/idioms', methods=['POST', 'GET'])
def idioms():
    if request.method == 'POST':
        name = request.form.get('name')

        # group_id здесь может быть ''
        group_id = request.form.get('group')
        if group_id == '':
            group_id = None

        if get_idioms(name=name):
            message = 'existing idiom'
        else:
            add_idiom(name=name, group_id=group_id)
            message = 'success'

    idioms = get_idioms()
    tree_data = {}

    # Создаем данные для дерева
    for idiom in idioms:
        idiom_data = {'name': idiom.name,
                      'group': idiom.group.name if idiom.group else 'Языки',
                      'corpora': []}
        for corpus in idiom.corpora:
            corpus_link = f'<a href="/corpora/{corpus.id}">{corpus.name}</a>'
            idiom_data['corpora'].append(corpus_link)
        if idiom.group_id not in tree_data:
            tree_data[idiom.group_id] = {'name': idiom.group.name
                                         if idiom.group else 'Языки',
                                         'children': []}
        tree_data[idiom.group_id]['children'].append(idiom_data)

    # Функция для создания дерева
    def create_tree(tree_nodes, node):
        if 'children' in node:
            for child in node['children']:
                create_tree(tree_nodes, child)
        if 'group' in node or node.get('name') == 'Языки':
            print(tree_nodes)
            tree_nodes['labels'].append(node['name'])
            tree_nodes['parents'].append(node.get('group'))
            tree_nodes['customdata'].append(node.get('corpora'))

    tree_nodes = {'labels': [], 'parents': [],
                  'customdata': []}
    create_tree(tree_nodes, {'children': list(tree_data.values())})
    treemap = go.Treemap(
        labels=tree_nodes['labels'],
        parents=tree_nodes['parents'],
        # Добавляем информацию о корпусах в пользовательские данные
        customdata=tree_nodes['customdata'],
        hovertemplate="<b>%{label}</b><br><br>" +
        "Corpora: %{customdata}<br>" +
        "<extra></extra>",
    )

    # Создание дерева
    fig = go.Figure(
        data=treemap)
    fig.update_traces(root_color="lightgrey")
    fig.update_layout(
        title='Дерево языков',
        margin=dict(t=50, l=25, r=25, b=25),
    )

    # Возвращаем интерактивное дерево в виде HTML
    tree_html = fig.to_html(full_html=False, include_plotlyjs='cdn')

    message = ''
    return render_template('idioms.html', idioms=idioms,
                           message=message, tree_html=tree_html)


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        login = request.form.get('login')
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        # Validating login and password
        if find_user(login):
            return render_template('signup.html', message='existing login')
        if find_user(email):
            return render_template('signup.html', message='existing email')

        # Hash password
        hashed_password = bcrypt.generate_password_hash(
            password
                ).decode("utf-8")

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

        message = 'wrong password'
    else:
        message = 'invalid login'

    # Failed login
    return render_template('signin.html', message=message)


if __name__ == '__main__':
    app.run(host=HOST, port=PORT, debug=True)
