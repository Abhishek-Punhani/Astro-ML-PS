from flask import jsonify, session
from db import get_db
from models.user import User as users

def get_user_profile():
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({"error": "Unauthorized access"}), 401

        db = get_db()
        user = db.query(users).filter(users.id == user_id).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        return jsonify({
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email
            }
        }), 200
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500
