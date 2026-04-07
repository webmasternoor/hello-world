from flask import Flask, request, jsonify, g
from flask_cors import CORS
import mysql.connector
from mysql.connector import errorcode, IntegrityError

app = Flask(__name__)
CORS(app)

# MySQL configuration
MYSQL_CONFIG = {
    'user': 'your_mysql_user',
    'password': 'your_mysql_password',
    'host': 'localhost',
    'database': 'mydatabase',
    'raise_on_warnings': True
}

# Connect to DB helper
def get_db():
    if 'db' not in g:
        g.db = mysql.connector.connect(**MYSQL_CONFIG)
    return g.db

# Close DB connection after request
@app.teardown_appcontext
def close_connection(exception):
    db = g.pop('db', None)
    if db is not None and db.is_connected():
        db.close()

# Initialize DB and create users table if not exists
def init_db():
    db = mysql.connector.connect(
        user=MYSQL_CONFIG['user'],
        password=MYSQL_CONFIG['password'],
        host=MYSQL_CONFIG['host']
    )
    cursor = db.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_CONFIG['database']}")
    db.database = MYSQL_CONFIG['database']

    create_table_query = '''
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL
        )
    '''
    cursor.execute(create_table_query)
    db.commit()
    cursor.close()
    db.close()

init_db()

# Helper to convert MySQL row to dict
def user_to_dict(row):
    # row is a tuple (id, username, password)
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

    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute('INSERT INTO users (username, password) VALUES (%s, %s)', (username, password))
        db.commit()
        user_id = cursor.lastrowid
        cursor.execute('SELECT id, username FROM users WHERE id = %s', (user_id,))
        user = cursor.fetchone()
        cursor.close()
        return jsonify(user_to_dict(user)), 201
    except IntegrityError as err:
        cursor.close()
        if err.errno == errorcode.ER_DUP_ENTRY:
            return jsonify({'error': 'username already exists'}), 409
        return jsonify({'error': 'database error'}), 500

# Read all users
@app.route('/users', methods=['GET'])
def get_users():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT id, username FROM users')
    users = cursor.fetchall()
    cursor.close()
    return jsonify([user_to_dict(user) for user in users])

# Read user by id
@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT id, username FROM users WHERE id = %s', (user_id,))
    user = cursor.fetchone()
    cursor.close()
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

    db = get_db()
    cursor = db.cursor()
    cursor.execute('UPDATE users SET password = %s WHERE id = %s', (new_password, user_id))
    db.commit()
    rowcount = cursor.rowcount
    cursor.close()
    if rowcount == 0:
        return jsonify({'error': 'user not found'}), 404
    return jsonify({'message': 'password updated'})

# Delete user
@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    db = get_db()
    cursor = db.cursor
