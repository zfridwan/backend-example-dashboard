from flask import Flask, request, jsonify, session, send_from_directory
from flask_mysqldb import MySQL
from flask_cors import CORS
from datetime import timedelta, datetime
import os

app = Flask(__name__)

CORS(app, supports_credentials=True)

# Database Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'mydb'

# Secret Key for Session Management
app.secret_key = 'your-secret-key'

# Set session lifetime to 15 minutes
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=15)

# Initialize MySQL
mysql = MySQL(app)

# Folder for Text Files
TEXT_FILE_FOLDER = 'D:/text'

# Middleware to check and update session activity
@app.before_request
def update_session_activity():
    if 'user_id' in session:
        last_active = session.get('last_active')
        now = datetime.utcnow()
        
        # Check if session has been inactive for more than 15 minutes
        if last_active and (now - datetime.fromisoformat(last_active)).total_seconds() > 900:
            session.clear()
            return jsonify({'message': 'Session timed out. Please log in again.'}), 401
        
        # Update last active time
        session['last_active'] = now.isoformat()

# Login Route
@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')

    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()

        if user:
            session.permanent = True  # Enable session timeout
            session['user_id'] = user[0]  # Assuming user ID is the first column
            session['username'] = user[1]  # Assuming username is the second column
            session['role'] = user[3]  # Assuming role is the fourth column
            session['last_active'] = datetime.utcnow().isoformat()

            return jsonify({
                'message': 'Login Sukses',
                'role': user[3]
            }), 200
        else:
            return jsonify({
                'message': 'username atau password salah'
            }), 401

    except Exception as e:
        return jsonify({
            'message': 'Error saat memproses permintaan.',
            'error': str(e)
        }), 500

# Session Check Route
@app.route('/session', methods=['GET'])
def check_session():
    if 'user_id' in session:
        return jsonify({
            'isAuthenticated': True,
            'role': session['role'],
            'username': session['username']
        }), 200
    else:
        return jsonify({
            'isAuthenticated': False
        }), 401

# Buat User Baru Route
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

# Download Route
@app.route('/download')
def download_file():
    filename = 'react.txt'
    try:
        return send_from_directory(TEXT_FILE_FOLDER, filename, as_attachment=True)
    except FileNotFoundError:
        return "File tidak ada", 404

# Logout Route
@app.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return jsonify({
        'message': 'Logged out berhasil'
    }), 200

# Laporan Route
@app.route('/api/financial-report', methods=['GET'])
def get_financial_report():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    cursor = mysql.connection.cursor()
    query = """SELECT * FROM financial_data WHERE date BETWEEN %s AND %s"""
    cursor.execute(query, (start_date, end_date))
    results = cursor.fetchall()

    reports = [{'id': row[0], 'date': row[1], 'revenue': row[2], 'expense': row[3]} for row in results]
    
    return jsonify(reports)

# Menjalankan Aplikasi
if __name__ == '__main__':
    app.run(debug=True, port=5000)
