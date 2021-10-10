import datetime
import os
import sqlite3

from flask import Flask, g, render_template, request, flash, session, redirect, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from hw_1.flaskdatabase import FlaskDataBase

DATABASE = 'flaskapp.db'
DEBUG = True
SECRET_KEY = 'sfhiugbdsaaiddsan'

app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(DATABASE=os.path.join(app.root_path, 'flaskapp.db')))
app.permanent_session_lifetime = datetime.timedelta(days=1)


def create_db():
    """Creates database from sql file"""
    db = connect_db()
    with app.open_resource('db_schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()


def connect_db():
    """Returns connection to a database"""
    conn = sqlite3.connect(app.config['DATABASE'])

    # Without this db will return rows as tuples, with this - as dict
    conn.row_factory = sqlite3.Row
    return conn


def get_db():
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db


fdb = None


@app.before_request
def before_request_func():
    global fdb
    fdb = FlaskDataBase(get_db())
    print('BEFORE REQUEST called!')


@app.route('/')
def index():
    if 'logged' in session:
        return render_template('index.html', logged=session['logged'], name=session['email'])
    else:
        return render_template('index.html')


@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            flash('Empty fields!', category='error')
        elif len(password) < 8:
            flash('Password too short!', category='error')
        elif '@' not in email or '.' not in email:
            flash('Invalid email!', category='error')

        if not email:
            email = ''
        if not password:
            password = ''

        user = fdb.get_user(email)
        if user:
            if check_password_hash(user['password'], password):
                session['logged'] = True
                session['email'] = email
                flash('Success!', category='success')
            else:
                flash('Incorrect data!', category='error')
        else:
            flash('Incorrect data!', category='error')

        if 'logged' in session:
            return render_template('login.html', email=email, password=password, logged=session['logged'],
                                   name=session['email'])
        else:
            return render_template('login.html', email=email, password=password)
    elif request.method == "GET":
        if 'logged' in session:
            return render_template('login.html', email='', password='', logged=session['logged'],
                                   name=session['email'])
        else:
            return render_template('login.html', email='', password='')
    else:
        raise Exception(f"Method {request.method} is not allowed!")


@app.route('/signup', methods=["POST", "GET"])
def signup():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            flash('Empty fields!', category='error')
        elif len(password) < 8:
            flash('Password too short!', category='error')
        elif '@' not in email or '.' not in email:
            flash('Invalid email!', category='error')

        if not email:
            email = ''
        if not password:
            password = ''

        res = fdb.add_user(email, generate_password_hash(password))
        if not res:
            flash('User was not added. Unexpected error.', category='error')
        else:
            flash('Success!', category='success')
        if 'logged' in session:
            return render_template('signup.html', email=email, password=password, logged=session['logged'],
                                   name=session['email'])
        else:
            return render_template('signup.html', email=email, password=password)
    elif request.method == "GET":
        if 'logged' in session:
            return render_template('signup.html', email='', password='', logged=session['logged'],
                                   name=session['email'])
        else:
            return render_template('signup.html', email='', password='')
    else:
        raise Exception(f"Method {request.method} is not allowed!")


@app.route('/logout/<page>')
def logout(page):
    session['logged'] = False
    session['email'] = ''
    return redirect(url_for(page))


if __name__ == '__main__':
    app.run(debug=True)
