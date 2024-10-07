import re
import bcrypt
import json
from email_validator import validate_email, EmailNotValidError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from models.user import User as users
from db import get_auth_db
from config_redis import redis_client


def user_to_dict(user):
    return {
        "id": str(user.id),
        "email": user.email,
        "password": user.password,
        "username": user.username,
        "isVerified": user.isVerified,
        "peak_result_ids": [str(id) for id in user.peak_result_ids],
    }


async def create_user(userData):
    db: Session = get_auth_db()
    try:
        username = userData.get("username")
        email = userData.get("email")
        password = userData.get("password")
        auth_id = userData.get("authId")
        # Check if fields are empty
        if not username or not email:
            return {"error": "Please fill all fields."}

        # Check username length
        if len(username) < 2 or len(username) > 16:
            return {
                "error": "Please make sure your username is between 2 and 16 characters."
            }

        # Validate email
        try:
            validate_email(email)
        except EmailNotValidError:
            return {"error": "Please provide a valid email address."}

        # Cache key for the user based on email
        cache_key = f"user:{email}"

        # Check if user data exists in Redis cache
        cached_user = redis_client.get(cache_key)

        if cached_user is not None:
            existing_user = json.loads(cached_user)
            if existing_user:
                return {
                    "error": "This email already exists. Please try with a different email."
                }

        else:
            existing_user = db.query(users).filter_by(email=email).first()
            if existing_user is not None:
                user_dict = user_to_dict(existing_user)
                redis_client.setex(cache_key, 84000, json.dumps(user_dict))
        if existing_user:
            return {
                "error": "This email already exists. Please try with a different email."
            }

        # Check password or Google ID
        if not password:
            if not auth_id:
                return {"error": "Please provide either a password or a Google ID."}
            password = auth_id

        # Check password length
        if password and len(password) < 6 or len(password) > 128:
            return {
                "error": "Please ensure your password is between 6 and 128 characters."
            }

        if (
            password
            and not auth_id
            and not re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\W).+$", password)
           ):
            return {
                "error": "Password must contain at least one uppercase letter, one lowercase letter, and one special character."
            }

        # Hash password or Google ID
        hashed_password = bcrypt.hashpw(
            password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

        # Add new user to the database
        new_user = users(username=username, email=email, password=hashed_password)

        db.add(new_user)
        db.commit()
        return user_to_dict(new_user)

    except IntegrityError:
        db.rollback()
        return {"error": "Database error. Please try again."}
    except Exception as e:
        return {"error": str(e)}
