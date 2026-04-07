from flask import Flask, request, jsonify, g
import psycopg2
import psycopg2.extras
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# PostgreSQL configuration
PG_CONFIG = {
    'host': 'localhost',
    'database': 'mydatabase',
    'user': 'your_pg_user',
    'password': 'your_pg_password',
}

# Connect to DB helper, store connection in Flask's `g`
def get_db():
    if 'db' not in g:
        g.db = psycopg2.connect(**PG_CONFIG)
    return g.db

# Close DB after request
@app.teardown_appcontext
def close_connection(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

# Initialize DB and create users table if not exists
def init_db():
    conn = psycopg2.connect(
        host=PG_CONFIG['host'],
        user=PG_CONFIG['user'],
        password=PG_CONFIG['password'],
        dbname='postgres'  # connect to default db to create target db
    )
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute(f"CREATE DATABASE {PG_CONFIG['database']}")
    cur.close()
    conn.close()

    # Now connect to the target database and create table
    conn = psycopg2.connect(**PG_CONFIG)
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL
        )
    ''')
    conn.commit()
    cur.close()
    conn.close()

# Try to create database, ignore errors if it exists
try:
    init_db()
except psycopg2.errors.DuplicateDatabase:
    pass
except Exception as e:
    # You may want to log or raise to detect other critical issues
    print(f"DB init error: {e}")

# Helper to convert row to dict
def user_to_dict(row):
    if row is None:
        return None
    return {
        'id': row[0],
        'username': row[1]
    }

# Create user
@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'username and password required'}), 400

    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute('INSERT INTO users (username, password) VALUES (%s, %s) RETURNING id, username',
                    (username, password))
        user = cur.fetchone()
        conn.commit()
        cur.close()
        return jsonify(user_to_dict(user)), 201
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        cur.close()
        return jsonify({'error': 'username already exists'}), 409
    except Exception as e:
        conn.rollback()
        cur.close()
        return jsonify({'error': f'database error: {str(e)}'}), 500

# Read all users
@app.route('/users', methods=['GET'])
def get_users():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT id, username FROM users')
    users = cur.fetchall()
    cur.close()
    return jsonify([user_to_dict(user) for user in users])

# Read user by id
@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT id, username FROM users WHERE id = %s', (user_id,))
    user = cur.fetchone()
    cur.close()
    if not user:
        return jsonify({'error': 'user not found'}), 404
    return jsonify(user_to_dict(user))

# Update user password
@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()
    new_password = data.get('password')
    if not new_password:
        return jsonify({'error': 'password required'}), 400

    conn = get_db()
    cur = conn.cursor()
    cur.execute('UPDATE users SET password = %s WHERE id = %s', (new_password, user_id
