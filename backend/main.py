from flask import Flask, request, session, jsonify, make_response
from flask_cors import CORS
from flask_session import Session
from db import get_db  
from model import User as users
import os
import json
from datetime import timedelta
import dotenv
import bcrypt
import jwt

dotenv.load_dotenv()  

app = Flask(__name__)

# CORS configuration
cors_options = {
    "supports_credentials": True
}
CORS(app, resources={r"/*": cors_options})

# Session configuration
app.config["SECRET_KEY"] = os.getenv("SECRET")
app.config["SESSION_TYPE"] = "filesystem"  
app.config["SESSION_PERMANENT"] = True
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=7)

Session(app)

# Middleware for logging requests
@app.before_request
def before_request():
    if app.debug:
        app.logger.debug(f"Request: {request.method} {request.url}")

# Register user route
@app.route("/auth/register", methods=["POST"])
def register():
    try:
        db = get_db()
        data = request.get_json()

        if not data or 'username' not in data or 'email' not in data or 'password' not in data:
            return jsonify({"error": "Missing required fields."}), 400

        username = data['username']
        email = data['email']
        password = data['password']

        existing_user = db.query(users).filter(users.email == email).first()
        if existing_user:
            return jsonify({"error": "User already exists"}), 400

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        new_user = users(
            email=email,
            password=hashed_password,
            username=username,
        )

        db.add(new_user)
        db.commit()
        
        # Generate JWT tokens
        access_token = jwt.encode({"userId": new_user.id}, os.getenv("AUTH_SECRET"), algorithm="HS256")
        refresh_token = jwt.encode({"userId": new_user.id}, os.getenv("REFRESH_TOKEN_SECRET"), algorithm="HS256")

        # Decode tokens to strings
        access_token_str = access_token if isinstance(access_token, str) else access_token.decode('utf-8')
        refresh_token_str = refresh_token if isinstance(refresh_token, str) else refresh_token.decode('utf-8')

        # Response Structure
        response_data = {
            "message": "Register success.",
            "user": {
                "id": new_user.id,
                "username": new_user.username,
                "email": new_user.email,
                "token": access_token_str,
            },
        } 

        return jsonify(response_data)
    except Exception as e:
        app.logger.error("Error in /auth/register: %s", e)
        return jsonify({"error": "Internal server error"}), 500

@app.route("/auth/login", methods=["POST"])
def login():
    try:
        db = get_db()
        data = request.get_json()
        email = data['email']
        password = data['password']

        user = db.query(users).filter(users.email == email).first()
        if not user or not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            return jsonify({"error": "Invalid credentials"}), 401

        access_token = jwt.encode({"userId": user.id}, os.getenv("AUTH_SECRET"), algorithm="HS256")
        refresh_token = jwt.encode({"userId": user.id}, os.getenv("REFRESH_TOKEN_SECRET"), algorithm="HS256")

        access_token_str = access_token if isinstance(access_token, str) else access_token.decode('utf-8')
        refresh_token_str = refresh_token if isinstance(refresh_token, str) else refresh_token.decode('utf-8')

        # Response Structure
        response_data = {
            "message": "Login success.",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "token": access_token_str,
            },
        } 

        return jsonify(response_data)
    except Exception as e:
        app.logger.error("Error in /auth/login: %s", e)
        return jsonify({"error": "Internal server error"}), 500

@app.route("/auth/refreshtoken", methods=["POST"])
def refresh_token():
    try:
        db = get_db()
        refresh_token = request.cookies.get("refreshtoken")
        if not refresh_token:
            return jsonify({"error": "Please login."}), 401

        check = jwt.decode(refresh_token, os.getenv("REFRESH_TOKEN_SECRET"), algorithms=["HS256"])
        user = db.query(users).filter(users.id == check['userId']).first()
        if not user:
            return jsonify({"error": "User not found."}), 404

        access_token = jwt.encode({"userId": user.id}, os.getenv("AUTH_SECRET"), algorithm="HS256")

        access_token_str = access_token if isinstance(access_token, str) else access_token.decode('utf-8')

        return jsonify({
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "token": access_token_str,
            },
        })
    except Exception as e:
        app.logger.error("Error in /auth/refreshtoken: %s", e)
        return jsonify({"error": "Internal server error"}), 500

# Logout route
@app.route("/auth/logout", methods=["POST"])
def logout():
    try:
        response = make_response(jsonify({"message": "Logged out successfully."}))
        response.delete_cookie("refreshtoken", path="/api/auth/refreshtoken")
        return response
    except Exception as e:
        app.logger.error("Error in /auth/logout: %s", e)
        return jsonify({"error": "Internal server error"}), 500

# Error handling
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"error": {"status": 404, "message": "Page Not Found!"}}), 404

@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({"error": {"status": 500, "message": "Internal Server Error!"}}), 500

# Main app execution
if __name__ == "__main__":
    app.run(debug=True, port=8080)
