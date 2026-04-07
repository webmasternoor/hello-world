from flask import Flask, request, jsonify, g
import sqlite3
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
DATABASE = 'users.db'

# Connect to DB helper
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

# Close DB after request
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db:
        db.close()

# Initialize DB and create users table
def init_db():
    with app.app_context():
        db = get_db()
        db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        db.commit()

init_db()

# Create user
@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'username and password required'}), 400

    db = get_db()
    try:
        db.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        db.commit()
        user = db.execute('SELECT id, username FROM users WHERE username = ?', (username,)).fetchone()
        return jsonify(dict(user)), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'username already exists'}), 409

# Read all users
@app.route('/users', methods=['GET'])
def get_users():
    db = get_db()
    users = db.execute('SELECT id, username FROM users').fetchall()
    return jsonify([dict(user) for user in users])

# Read user by id
@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    db = get_db()
    user = db.execute('SELECT id, username FROM users WHERE id = ?', (user_id,)).fetchone()
    if user:
        return jsonify(dict(user))
    return jsonify({'error': 'user not found'}), 404

# Update user password
@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()
    password = data.get('password')
    if not password:
        return jsonify({'error': 'password required'}), 400

    db = get_db()
    cursor = db.execute('UPDATE users SET password = ? WHERE id = ?', (password, user_id))
    db.commit()
    if cursor.rowcount == 0:
        return jsonify({'error': 'user not found'}), 404
    return jsonify({'message': 'password updated'})

# Delete user
@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    db = get_db()
    cursor = db.execute('DELETE FROM users WHERE id = ?', (user_id,))
    db.commit()
    if cursor.rowcount == 0:
        return jsonify({'error': 'user not found'}), 404
    return jsonify({'message': 'user deleted'})

if __name__ == '__main__':
    app.run(debug=True)
