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


# app.secret_key = ''

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
            # user info in session
            session['user_id'] = user[0]  # kolom user id
            session['username'] = user[1]  # kolom username
            session['role'] = user[3]  # kolom role

            # Pesan balikan jika user berhasil login berdasarkan role
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
            'message': 'error ketika memproses permintaan.',
            'error': str(e)
        }), 500

@app.route('/session', methods=['GET'])
def check_session():
    # Chek session login jika user berhasil
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
    # membersihkan session user jika berhasil logout
    session.clear()
    return jsonify({
        'message': 'Logged out berhasil'
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
            'message': 'User berhasil dibuat'
        }), 201

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return jsonify({
            'message': 'error ketika membuat user baru',
            'error': str(e)
        }), 500

@app.route('/download')
def download_file():
    filename = 'react.txt'
    try:
        return send_from_directory(TEXT_FILE_FOLDER, filename, as_attachment=True)
    except FileNotFoundError:
        return "File tidak ada", 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)
