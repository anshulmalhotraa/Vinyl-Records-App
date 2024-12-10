from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
import os

app = Flask(__name__)

# Fetch secret key from AWS Systems Manager Parameter Store
def get_secret_key():
    try:
        ssm = boto3.client('ssm', region_name='eu-west-1')  # Use the region where your parameter is stored
        parameter = ssm.get_parameter(Name='/flask/secret_key', WithDecryption=True)
        return parameter['Parameter']['Value']
    except (NoCredentialsError, PartialCredentialsError):
        # Fallback for local development
        return "default_key"

# Set the secret key
app.secret_key = get_secret_key()

# Database initialization
def init_db():
    db_path = os.path.join(os.path.dirname(__file__), "vinyl_records.db")
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Create users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    # Create records table
    c.execute('''
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            album_name TEXT NOT NULL,
            artist TEXT NOT NULL,
            year INTEGER,
            condition TEXT,
            user_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    conn.commit()
    conn.close()

# Login decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in first.')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), "vinyl_records.db"))
        c = conn.cursor()

        try:
            c.execute('INSERT INTO users (username, password) VALUES (?, ?)',
                      (username, generate_password_hash(password)))
            conn.commit()
            flash('Registration successful! Please login.')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists!')
        finally:
            conn.close()

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), "vinyl_records.db"))
        c = conn.cursor()

        c.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = c.fetchone()
        conn.close()

        if user and check_password_hash(user[2], password):
            session['user_id'] = user[0]
            session['username'] = user[1]
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password!')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), "vinyl_records.db"))
    c = conn.cursor()

    c.execute('SELECT * FROM records WHERE user_id = ?', (session['user_id'],))
    records = c.fetchall()
    conn.close()

    return render_template('dashboard.html', records=records)

@app.route('/add_record', methods=['GET', 'POST'])
@login_required
def add_record():
    if request.method == 'POST':
        album_name = request.form['album_name']
        artist = request.form['artist']
        year = request.form['year']
        condition = request.form['condition']

        conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), "vinyl_records.db"))
        c = conn.cursor()

        c.execute('''INSERT INTO records (album_name, artist, year, condition, user_id)
                     VALUES (?, ?, ?, ?, ?)''',
                  (album_name, artist, year, condition, session['user_id']))
        conn.commit()
        conn.close()

        flash('Record added successfully!')
        return redirect(url_for('dashboard'))

    return render_template('add_record.html')

@app.route('/edit_record/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_record(id):
    conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), "vinyl_records.db"))
    c = conn.cursor()

    if request.method == 'POST':
        album_name = request.form['album_name']
        artist = request.form['artist']
        year = request.form['year']
        condition = request.form['condition']

        c.execute('''UPDATE records 
                     SET album_name = ?, artist = ?, year = ?, condition = ?
                     WHERE id = ? AND user_id = ?''',
                  (album_name, artist, year, condition, id, session['user_id']))
        conn.commit()
        flash('Record updated successfully!')
        return redirect(url_for('dashboard'))

    c.execute('SELECT * FROM records WHERE id = ? AND user_id = ?',
              (id, session['user_id']))
    record = c.fetchone()
    conn.close()

    if record is None:
        flash('Record not found!')
        return redirect(url_for('dashboard'))

    return render_template('edit_record.html', record=record)

@app.route('/delete_record/<int:id>')
@login_required
def delete_record(id):
    conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), "vinyl_records.db"))
    c = conn.cursor()

    c.execute('DELETE FROM records WHERE id = ? AND user_id = ?',
              (id, session['user_id']))
    conn.commit()
    conn.close()

    flash('Record deleted successfully!')
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)  # Production-ready configuration
