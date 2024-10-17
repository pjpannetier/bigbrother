from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from mysql.connector import pooling
from datetime import datetime
import os
from dotenv import load_dotenv
from openai import OpenAI
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import SQLAlchemyError

load_dotenv()

app = Flask(__name__)
CORS(app)

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Database connection pool configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'bigbrother',
    'port': 3306
}

# Create a connection pool
connection_pool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name="mypool",
    pool_size=5,
    **db_config
)

def get_db_connection():
    return connection_pool.get_connection()

def execute_query(query, params=None):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(query, params)
        result = cursor.fetchall()
        connection.commit()
        return result
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()

def calculate_message_score(message):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an AI that analyzes messages and assigns a score from 0 to 100 based on how positive and supportive the message is."},
                {"role": "user", "content": f"Please analyze this message and give it a score from 0 to 100: '{message}' You should only output the score, and nothing else."}
            ]
        )
        score_text = response.choices[0].message.content
        score = float(score_text.split()[0])
        return min(max(score, 0), 100), False  # Return score and flag
    except Exception as e:
        print(f"Error calculating message score: {str(e)}")
        return 50.0, True  # Return default score and set flag to True

@app.route('/api/users', methods=['GET'])
def get_data():
    try:
        query = """
            SELECT *
            FROM users u
            LEFT JOIN identities i ON u.id = i.user_id
        """
        rows = execute_query(query)
        return jsonify(rows), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/message', methods=['POST'])
def add_message():
    try:
        data = request.json
        
        required_fields = ['username', 'message']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400   
        
        user_query = "SELECT id FROM users WHERE username = %s"
        user = execute_query(user_query, (data['username'],))
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        message_score, flag = calculate_message_score(data['message'])
        
        insert_query = """
            INSERT INTO messages (user_id, message, date, score, flagged)
            VALUES (%s, %s, %s, %s, %s)
        """
        execute_query(insert_query, (user[0]['id'], data['message'], datetime.now(), message_score, flag))
        
        update_query = """
            UPDATE users u
            SET score = (
                SELECT AVG(score)
                FROM messages
                WHERE user_id = u.id
            )
            WHERE id = %s
        """
        execute_query(update_query, (user[0]['id'],))
        
        return jsonify({"message": "Message added successfully", "score": message_score}), 201
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/messages', methods=['GET'])
def get_messages():
    try:
        username = request.args.get('user')
        
        if username:
            query = """
                SELECT m.id, u.username, m.message, m.date, m.score, m.flagged
                FROM messages m
                JOIN users u ON m.user_id = u.id
                WHERE u.username = %s
                ORDER BY m.date DESC
            """
            messages = execute_query(query, (username,))
        else:
            query = """
                SELECT m.id, u.username, m.message, m.date, m.score, m.flagged
                FROM messages m
                JOIN users u ON m.user_id = u.id
                ORDER BY m.date DESC
            """
            messages = execute_query(query)

        if not messages:
            return jsonify({"message": "No messages found"}), 404

        return jsonify(messages), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/users/register', methods=['POST'])
def register_user():
    try:
        data = request.json
        required_fields = ['username', 'password']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        # Check if the username already exists
        check_query = "SELECT id FROM users WHERE username = %s"
        existing_user = execute_query(check_query, (data['username'],))
        if existing_user:
            return jsonify({"error": "Username already exists"}), 409

        # Create new user
        password_hash = generate_password_hash(data['password'])
        insert_query = """
            INSERT INTO users (username, password_hash, score, under_investigation, under_surveillance, role)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        execute_query(insert_query, (data['username'], password_hash, 0.0, False, False, 'user'))

        return jsonify({"message": "User registered successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/users/login', methods=['POST'])
def login_user():
    try:
        data = request.json
        required_fields = ['username', 'password']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        # Get user by username
        query = "SELECT id, username, password_hash, role FROM users WHERE username = %s"
        user = execute_query(query, (data['username'],))

        if not user:
            return jsonify({"error": "User not found"}), 404

        user = user[0]
        if check_password_hash(user['password_hash'], data['password']):
            return jsonify({
                "message": "Login successful",
                "user_id": user['id'],
                "username": user['username'],
                "role": user['role']
            }), 200
        else:
            return jsonify({"error": "Invalid password"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/users/update_password', methods=['PUT'])
def update_password():
    try:
        data = request.json
        required_fields = ['username', 'old_password', 'new_password']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        # Get user by username
        query = "SELECT id, password_hash FROM users WHERE username = %s"
        user = execute_query(query, (data['username'],))

        if not user:
            return jsonify({"error": "User not found"}), 404

        user = user[0]
        if check_password_hash(user['password_hash'], data['old_password']):
            # Update password
            new_password_hash = generate_password_hash(data['new_password'])
            update_query = "UPDATE users SET password_hash = %s WHERE id = %s"
            execute_query(update_query, (new_password_hash, user['id']))

            return jsonify({"message": "Password updated successfully"}), 200
        else:
            return jsonify({"error": "Invalid old password"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/report', methods=['POST'])
def report_message():
    try:
        data = request.json
        required_fields = ['message_id', 'reporter_username']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        # Get reporter user ID
        reporter_query = "SELECT id FROM users WHERE username = %s"
        reporter = execute_query(reporter_query, (data['reporter_username'],))
        
        if not reporter:
            return jsonify({"error": "Reporter not found"}), 404

        # Check if the message exists and get user_id
        check_message_query = "SELECT id, user_id FROM messages WHERE id = %s"
        message = execute_query(check_message_query, (data['message_id'],))

        if not message:
            return jsonify({"error": "Message not found"}), 404

        # Update message to flagged and set score to 0
        update_query = """
            UPDATE messages
            SET flagged = TRUE, score = 0
            WHERE id = %s
        """
        execute_query(update_query, (data['message_id'],))

        # Update user's score
        update_user_score_query = """
            UPDATE users u
            SET score = (
                SELECT AVG(score)
                FROM messages
                WHERE user_id = u.id
            )
            WHERE id = %s
        """
        execute_query(update_user_score_query, (message[0]['user_id'],))

        return jsonify({"message": "Message reported and score updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/flagged-messages', methods=['GET'])
def get_flagged_messages():
    try:
        query = """
            SELECT m.id, u.username, m.message, m.date, m.score
            FROM messages m
            JOIN users u ON m.user_id = u.id
            WHERE m.flagged = TRUE
            ORDER BY m.date DESC
        """
        messages = execute_query(query)

        if not messages:
            return jsonify({"message": "No flagged messages found"}), 404

        return jsonify(messages), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/messages/<int:message_id>', methods=['DELETE'])
def delete_message(message_id):
    try:
        # Check if the user is authenticated and is an administrator
        if 'username' not in request.headers:
            return jsonify({"error": "Authentication required"}), 401

        username = request.headers['username']
        user_query = "SELECT role FROM users WHERE username = %s"
        user = execute_query(user_query, (username,))

        if not user or user[0]['role'] != 'administrator':
            return jsonify({"error": "Administrator access required"}), 403

        # Check if the message exists
        check_message_query = "SELECT id FROM messages WHERE id = %s"
        message = execute_query(check_message_query, (message_id,))

        if not message:
            return jsonify({"error": "Message not found"}), 404

        # Delete the message
        delete_query = "DELETE FROM messages WHERE id = %s"
        execute_query(delete_query, (message_id,))

        return jsonify({"message": "Message deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
