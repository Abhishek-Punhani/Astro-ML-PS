import re
import bcrypt
from email_validator import validate_email, EmailNotValidError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from models.user import User as users
from db import get_auth_db


async def create_user(userData):
    db :Session= get_auth_db()
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


       
        # Check if user already exists
        existing_user = db.query(users).filter_by(email=email).first()
        print(existing_user)
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

        if password and not auth_id and not re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\W).+$", password):
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
        print(new_user.email)
        return new_user


    except IntegrityError:
        db.rollback()
        return {"error": "Database error. Please try again."}
    except Exception as e:
        return {"error": str(e)}
