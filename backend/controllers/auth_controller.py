from flask import jsonify, request, make_response, session
import bcrypt
import jwt
import os
from db import get_db
from models.user import User as users

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
        response = make_response(jsonify(response_data))
        response.set_cookie("xfd", refresh_token_str, httponly=True, path="/auth/refreshtoken", max_age=30*24*60*60, samesite="None", secure=True)
        return response
    except Exception as e:
        print("Error in /auth/register: %s", e)
        return jsonify({"error": "Internal server error"}), 500

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
        response = make_response(jsonify(response_data))
        response.set_cookie("xfd", refresh_token_str, httponly=True, path="/auth/refreshtoken", max_age=30*24*60*60, samesite="Lax", secure=True)
        return response
    except Exception as e:
        print("Error in /auth/login: %s", e)
        return jsonify({"error": "Internal server error"}), 500

def refresh_token():
    try:
        db = get_db()
        refresh_token = request.cookies.get("xfd")
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
        print("Error in /auth/refreshtoken: %s", e)
        return jsonify({"error": "Internal server error"}), 500
def logout():
    try:
        response = make_response(jsonify({"message": "Logged out successfully."}))
        response.delete_cookie("xfd", path="/auth/refreshtoken")
        return response
    except Exception as e:
        print("Error in /auth/logout: %s", e)
        return jsonify({"error": "Internal server error"}), 500

def google_login():
    try:
        db = get_db()
        data = request.get_json()

        # Extracting necessary parameters from the request body
        email = data.get('email')
        username = data.get('username')
        googleId = data.get('googleId')

        # Validate required fields
        if not all([email, username, googleId]):
            return jsonify({"error": "Missing required fields."}), 400

        # Check if the user already exists using email
        existing_user = db.query(users).filter(users.email == email).first()

        if not existing_user:
            # User does not exist, create a new one
            hashed_googleId = bcrypt.hashpw(googleId.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            new_user = users(
                email=email,
                username=username,
                password=hashed_googleId  # Store a hashed version of googleId
            )
            db.add(new_user)
            db.commit()
            user = new_user
        else:
            # User exists, log them in
            user = existing_user

        # Generate JWT tokens
        access_token = jwt.encode({"userId": user.id}, os.getenv("AUTH_SECRET"), algorithm="HS256")
        refresh_token = jwt.encode({"userId": user.id}, os.getenv("REFRESH_TOKEN_SECRET"), algorithm="HS256")

        # Decode tokens to strings
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
        response = make_response(jsonify(response_data))
        response.set_cookie("xfd", refresh_token_str, httponly=True, path="/auth/refreshtoken", max_age=30*24*60*60, samesite="None", secure=True)
        return response

    except Exception as e:
        print("Error in /auth/google-login: %s", e)
        return jsonify({"error": "Internal server error"}), 500

def change_password():
        try:
            db = get_db()
            data = request.get_json()

            if not data or 'current_password' not in data or 'new_password' not in data:
                return jsonify({"error": "Missing required fields."}), 400

            user_id = session.get('user_id')  # Assuming you store the user ID in session after login
            current_password = data['current_password']
            new_password = data['new_password']

            # Fetch the user from the database
            user = db.query(users).filter(users.id == user_id).first()
            if not user:
                return jsonify({"error": "User not found."}), 404

            # Verify the current password
            if not bcrypt.checkpw(current_password.encode('utf-8'), user.password.encode('utf-8')):
                return jsonify({"error": "Current password is incorrect."}), 401

            # Hash the new password
            hashed_new_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Update the user's password in the database
            user.password = hashed_new_password
            db.commit()

            return jsonify({"message": "Password changed successfully."}), 200

        except Exception as e:
            print("Error in /auth/change-password: %s", e)
            return jsonify({"error": "Internal server error"}), 500