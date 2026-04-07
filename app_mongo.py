from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from bson.objectid import ObjectId

app = Flask(__name__)
CORS(app)

# MongoDB setup
MONGODB_URI = 'mongodb://localhost:27017'  # change if needed
client = MongoClient(MONGODB_URI)
db = client['mydatabase']  # database name
users_collection = db['users']

# Create unique index on username
users_collection.create_index('username', unique=True)

# Helper to convert MongoDB document to JSON serializable dict
def user_to_dict(user_doc):
    return {
        'id': str(user_doc['_id']),
        'username': user_doc['username']
    }

# Create user
@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'username and password required'}), 400

    try:
        result = users_collection.insert_one({
            'username': username,
            'password': password
        })
        user_doc = users_collection.find_one({'_id': result.inserted_id})
        return jsonify(user_to_dict(user_doc)), 201
    except DuplicateKeyError:
        return jsonify({'error': 'username already exists'}), 409

# Read all users
@app.route('/users', methods=['GET'])
def get_users():
    users_cursor = users_collection.find({}, {'password': 0})  # exclude password
    users = [user_to_dict(user) for user in users_cursor]
    return jsonify(users)

# Read user by id
@app.route('/users/<user_id>', methods=['GET'])
def get_user(user_id):
    try:
        user_doc = users_collection.find_one({'_id': ObjectId(user_id)}, {'password': 0})
    except Exception:
        return jsonify({'error': 'invalid user id'}), 400

    if not user_doc:
        return jsonify({'error': 'user not found'}), 404
    return jsonify(user_to_dict(user_doc))

# Update user password
@app.route('/users/<user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()
    new_password = data.get('password')
    if not new_password:
        return jsonify({'error': 'password required'}), 400

    try:
        result = users_collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {'password': new_password}}
        )
    except Exception:
        return jsonify({'error': 'invalid user id'}), 400

    if result.matched_count == 0:
        return jsonify({'error': 'user not found'}), 404
    return jsonify({'message': 'password updated'})

# Delete user
@app.route('/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        result = users_collection.delete_one({'_id': ObjectId(user_id)})
    except Exception:
        return jsonify({'error': 'invalid user id'}), 400

    if result.deleted_count == 0:
        return jsonify({'error': 'user not found'}), 404
    return jsonify({'message': 'user deleted'})

if __name__ == '__main__':
    app.run(debug=True)
