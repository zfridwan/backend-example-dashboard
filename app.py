from flask import Flask, request, jsonify, session, send_from_directory
from flask_mysqldb import MySQL
from flask_cors import CORS
import os

app = Flask(__name__)

CORS(app, supports_credentials=True)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'mydb'

app.secret_key = 'your-secret-key'

mysql = MySQL(app)

TEXT_FILE_FOLDER = 'D:/text'

@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')

    try:
        print(f"Received login attempt for username: {username} with password: {password}")

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()

        if user:
            # Store user info in session
            session['user_id'] = user[0]  # Assuming the first column is the user ID
            session['username'] = user[1]  # Assuming the second column is the username
            session['role'] = user[3]  # Assuming the fourth column is the role

            # Return user role and success message
            print(f"User found: {user}")
            return jsonify({
                'message': 'Login Sukses',
                'role': user[3]
            }), 200
        else:
            print("Gagal username dan password.")
            return jsonify({
                'message': 'username atau password salah'
            }), 401

    except Exception as e:
        # Log the actual error for debugging
        print(f"Error occurred: {str(e)}")
        return jsonify({
            'message': 'An error occurred while processing your request.',
            'error': str(e)
        }), 500

@app.route('/session', methods=['GET'])
def check_session():
    # Check if the user is logged in via the session
    if 'user_id' in session:
        return jsonify({
            'isAuthenticated': True,
            'role': session['role'],
            'username': session['username']
        })
    else:
        return jsonify({
            'isAuthenticated': False
        }), 401

@app.route('/logout', methods=['GET'])
def logout():
    # Clear session to log out the user
    session.clear()
    return jsonify({
        'message': 'Logged out successfully'
    }), 200
    
@app.route('/create_user', methods=['POST'])
def create_user():
    username = request.json.get('username')
    password = request.json.get('password')
    role = request.json.get('role')

    try:
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)", (username, password, role))
        mysql.connection.commit()

        return jsonify({
            'message': 'User created successfully'
        }), 201

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return jsonify({
            'message': 'An error occurred while creating the user.',
            'error': str(e)
        }), 500

@app.route('/download')
def download_file():
    filename = 'react.txt'
    try:
        return send_from_directory(TEXT_FILE_FOLDER, filename, as_attachment=True)
    except FileNotFoundError:
        return "File not found", 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)
