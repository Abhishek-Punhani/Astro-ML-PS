import os
import random
from datetime import datetime, timezone, timedelta
from flask import jsonify, request, make_response
import requests
from sqlalchemy.exc import IntegrityError
import bcrypt
import jwt
from db import get_db
from models.user import User as users
from models.otp import OTP
from emails.verification import send_verification_email
from emails.forgotpass import send_reset_password_email
from utils.validation import create_user
from emails.verification import send_verification_email
from models.peakResult import PeakResult
from flask import jsonify, request, g

from sqlalchemy.orm import Session


async def register():
    try:
        db: Session = get_db()
        data = request.get_json()
        if (
            not data
            or "username" not in data
            or "email" not in data
            or "password" not in data
        ):
            return jsonify({"error": "Missing required fields."}), 400

        new_user = await create_user(data)
        if new_user is None:
            return jsonify({"error": "User creation failed."}), 500

        # Add the new user to the session and commit
        db.add(new_user)
        db.commit()
        db.refresh(new_user)  # Refresh the instance to ensure it's bound to the session

        token = jwt.encode(
            {
                "email": new_user.email,
                "exp": datetime.now(timezone.utc) + timedelta(seconds=330),
            },
            os.getenv("AUTH_SECRET"),
            algorithm="HS256",
        ).decode(
            "utf-8"
        )  # Convert token to UTF-8

        rtoken = jwt.encode(
            {
                "email": new_user.email,
                "exp": datetime.now(timezone.utc) + timedelta(minutes=20),
            },
            os.getenv("REFRESH_TOKEN_SECRET"),
            algorithm="HS256",
        ).decode("utf-8")

        # Generate a 6-digit OTP
        otp = random.randint(100000, 999999)

        # Convert OTP to string and append the token
        otp_with_token = f"{otp}-{token}"

        # Cleanup expired OTPs (older than 330 seconds)
        expiry_time = datetime.now(timezone.utc) - timedelta(seconds=330)
        db.query(OTP).filter(OTP.created_at < expiry_time).delete()

        # Check if an OTP entry already exists for this email and delete it
        existing_entry = db.query(OTP).filter(OTP.email == new_user.email).first()
        if existing_entry:
            db.delete(existing_entry)
            db.commit()

        # Create and save the new OTP entry with the modified OTP
        new_otp_entry = OTP(
            otp=otp_with_token,
            email=new_user.email,
            created_at=datetime.now(timezone.utc),
        )
        db.add(new_otp_entry)
        db.commit()

        # Send verification email (implement this function)
        send_verification_email(new_user.username, new_user.email, otp)

        # Respond with a success message and the token
        return (
            jsonify(
                {
                    "message": "OTP sent successfully.",
                    "token": token,
                    "ref_token": rtoken,
                }
            ),
            200,
        )

    except IntegrityError:
        db.rollback()
        return jsonify({"error": "An error occurred. Please try again."}), 500
    except Exception as e:
        print(f"Error in /auth/register: {e}")
        return jsonify({"error": "Internal server error"}), 500
    finally:
        db.close()


def login():
    try:
        db = get_db()
        data = request.get_json()
        if not data or "email" not in data or "password" not in data:
            return jsonify({"error": "Missing required fields."}), 400
        email = data["email"]
        password = data["password"]

        # Check for user credentials
        user = db.query(users).filter(users.email == email).first()
        if not user or not bcrypt.checkpw(
            password.encode("utf-8"), user.password.encode("utf-8")
        ):
            return jsonify({"error": "Invalid credentials"}), 401

        # Generate a unique token from email ID with 1-sec expiration
        token = jwt.encode(
            {
                "email": user.email,
                "exp": datetime.now(timezone.utc) + timedelta(seconds=330),
            },
            os.getenv("AUTH_SECRET"),
            algorithm="HS256",
        ).decode("utf-8")

        rtoken = jwt.encode(
            {
                "email": user.email,
                "exp": datetime.now(timezone.utc) + timedelta(minutes=20),
            },
            os.getenv("REFRESH_TOKEN_SECRET"),
            algorithm="HS256",
        ).decode("utf-8")

        # Generate a 6-digit OTP
        otp = random.randint(100000, 999999)

        # Convert OTP to string and append the token
        otp_with_token = f"{otp}-{token}"

        # Cleanup expired OTPs (older than 330 seconds)
        expiry_time = datetime.now(timezone.utc) - timedelta(seconds=330)
        db.query(OTP).filter(OTP.created_at < expiry_time).delete()

        # Check if an OTP entry already exists for this email and delete it
        existing_entry = db.query(OTP).filter(OTP.email == user.email).first()
        if existing_entry:
            db.delete(existing_entry)
            db.commit()

        # Create and save the new OTP entry with the modified OTP
        new_otp_entry = OTP(
            otp=otp_with_token, email=user.email, created_at=datetime.now(timezone.utc)
        )
        db.add(new_otp_entry)
        db.commit()

        # Send verification email (implement this function)
        send_verification_email(user.username, user.email, otp)

        # Respond with a success message and the token
        return (
            jsonify(
                {
                    "message": "OTP sent successfully.",
                    "token": token,
                    "ref_token": rtoken,
                }
            ),
            200,
        )

    except Exception as e:
        print(f"Error in /auth/login: {e}")
        return jsonify({"error": "Internal server error"}), 500


def refresh_token():
    try:
        db = get_db()
        refresh_token_cookie = request.cookies.get("xfd")
        if not refresh_token_cookie:
            return jsonify({"error": "Please login."}), 401

        check = jwt.decode(
            refresh_token_cookie,
            os.getenv("REFRESH_TOKEN_SECRET"),
            algorithms=["HS256"],
        )
        user = db.query(users).filter(users.id == check["userId"]).first()
        if not user:
            return jsonify({"error": "User not found."}), 404

        access_token = jwt.encode(
            {
                "userId": str(user.id),
                "exp": datetime.now(timezone.utc) + timedelta(days=1),
            },
            os.getenv("AUTH_SECRET"),
            algorithm="HS256",
        ).decode("utf-8")

        return jsonify(
            {
                "user": {
                    "id": str(user.id),
                    "username": user.username,
                    "email": user.email,
                    "token": access_token,
                },
            }
        )
    except Exception as e:
        print(f"Error in /auth/refreshtoken: {e}")
        return jsonify({"error": "Internal server error"}), 500


def logout():
    try:
        response = make_response(jsonify({"message": "Logged out successfully."}))
        response.delete_cookie("xfd", path="/auth/refreshtoken")
        return response
    except Exception as e:
        print(f"Error in /auth/logout: {e}")
        return jsonify({"error": "Internal server error"}), 500


async def google_login():
    try:
        db = get_db()
        data = request.get_json()

        # Extracting necessary parameters from the request body
        email = data.get("email")
        username = data.get("username")
        authId = data.get("authId")

        # Validate required fields
        if not all([email, username, authId]):
            return jsonify({"error": "Missing required fields."}), 400

        # Check if the user already exists using email
        existing_user = db.query(users).filter(users.email == email).first()

        if not existing_user:
            try:
                user = await create_user(data)
            except Exception as e:
                print(e)
                return jsonify({"error": "Internal server error"}), 500
        else:
            user = existing_user

        # Generate a unique token from email ID with 1-sec expiration
        token = jwt.encode(
            {
                "email": user.email,
                "exp": datetime.now(timezone.utc) + timedelta(seconds=330),
            },
            os.getenv("AUTH_SECRET"),
            algorithm="HS256",
        ).decode("utf-8")

        rtoken = jwt.encode(
            {
                "email": user.email,
                "exp": datetime.now(timezone.utc) + timedelta(minutes=20),
            },
            os.getenv("REFRESH_TOKEN_SECRET"),
            algorithm="HS256",
        ).decode("utf-8")

        # Generate a 6-digit OTP
        otp = random.randint(100000, 999999)

        # Convert OTP to string and append the token
        otp_with_token = f"{otp}-{token}"

        # Cleanup expired OTPs (older than 330 seconds)
        expiry_time = datetime.now(timezone.utc) - timedelta(seconds=330)
        db.query(OTP).filter(OTP.created_at < expiry_time).delete()

        # Check if an OTP entry already exists for this email and delete it
        existing_entry = db.query(OTP).filter(OTP.email == user.email).first()
        if existing_entry:
            db.delete(existing_entry)
            db.commit()

        # Create and save the new OTP entry with the modified OTP
        new_otp_entry = OTP(
            otp=otp_with_token, email=user.email, created_at=datetime.now(timezone.utc)
        )
        db.add(new_otp_entry)
        db.commit()

        # Send verification email (implement this function)
        send_verification_email(user.username, user.email, otp)

        # Respond with a success message and the token
        return (
            jsonify(
                {"message": "OTP sent successfully.", "token": token, "rtoken": rtoken}
            ),
            200,
        )

    except Exception as e:
        print(f"Error in /auth/google-login: {e}")
        return jsonify({"error": "Internal server error"}), 500


def verifyOtp():
    try:
        db = get_db()
        data = request.get_json()

        # Check if OTP and token are provided
        if not data or "otp" not in data or "token" not in data:
            return jsonify({"error": "Please provide both OTP and token."}), 400

        otp_received = data["otp"]
        token_received = data["token"]

        # Check if the token is a valid 6-digit number
        if not 100000 <= int(otp_received) <= 999999:
            return jsonify({"error": "Invalid OTP."}), 400

        # Convert OTP to string and append the token
        otp_with_token = f"{otp_received}-{token_received}"

        # Verify if the OTP exists in the database
        otp_entry = db.query(OTP).filter(OTP.otp == otp_with_token).first()
        if not otp_entry:
            return jsonify({"error": "Invalid OTP."}), 400

        # Check if the OTP is expired
        current_time = datetime.now(timezone.utc)
        otp_creation_time = otp_entry.created_at

        if otp_creation_time.tzinfo is None:
            otp_creation_time = otp_creation_time.replace(tzinfo=timezone.utc)

        time_difference = current_time - otp_creation_time
        if time_difference.total_seconds() > 330:
            db.delete(otp_entry)
            db.commit()
            return jsonify({"error": "OTP expired."}), 400

        try:
            jwt.decode(token_received, os.getenv("AUTH_SECRET"), algorithms=["HS256"])
        except Exception:
            return jsonify({"error": "Token expired."}), 400

        # Extract email from the OTP entry
        email = otp_entry.email

        # Delete the OTP entry after successful verification
        db.delete(otp_entry)
        db.commit()

        # Retrieve the user associated with the email
        user = db.query(users).filter(users.email == email).first()
        if not user:
            return jsonify({"error": "User not found."}), 404

        print(user.peak_result_ids)

        # Retrieve PeakResult objects for the user's peak_result_ids
        peak_results = (
            db.query(PeakResult).filter(PeakResult.id.in_(user.peak_result_ids)).all()
        )

        # Generate project names as an array of objects with id and project_name
        project_names = [
            {"id": str(result.id), "project_name": result.project_name}
            for result in peak_results
        ]

        # Generate JWT tokens
        access_token = jwt.encode(
            {"userId": str(user.id)}, os.getenv("AUTH_SECRET"), algorithm="HS256"
        )
        refresh_token = jwt.encode(
            {"userId": str(user.id)},
            os.getenv("REFRESH_TOKEN_SECRET"),
            algorithm="HS256",
        )

        # Decode tokens to strings
        access_token_str = (
            access_token
            if isinstance(access_token, str)
            else access_token.decode("utf-8")
        )
        refresh_token_str = (
            refresh_token
            if isinstance(refresh_token, str)
            else refresh_token.decode("utf-8")
        )

        # Response Structure
        response_data = {
            "message": "Login success.",
            "user": {
                "id": str(user.id),
                "username": user.username,
                "email": user.email,
                "token": access_token_str,
                "project_names": project_names,
            },
        }

        response = make_response(jsonify(response_data))
        response.set_cookie(
            "xfd",
            refresh_token_str,
            httponly=True,
            path="/auth/refreshtoken",
            max_age=30 * 24 * 60 * 60,
            samesite="None",
            secure=True,
        )

        return response

    except Exception as e:
        print(f"Error in /auth/otp: {e}")
        return jsonify({"error": "Internal server error"}), 500


def sendOtp():
    try:
        db = get_db()
        data = request.get_json()
        email = data["email"]

        # Check for user credentials
        user = db.query(users).filter(users.email == email).first()
        if not user:
            return jsonify({"error": "Invalid credentials"}), 401

        # Generate a unique token from email ID with 1-sec expiration
        token = jwt.encode(
            {
                "email": user.email,
                "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
            },
            os.getenv("AUTH_SECRET"),
            algorithm="HS256",
        ).decode("utf-8")
        clientapi = os.getenv("CLIENT_URI")
        link = clientapi + "/auth/newcredentials/" + str(user.id) + "/" + token
        send_reset_password_email(user.username, user.email, link)
        # Respond with a success message and the token
        return jsonify({"message": "Link sent successfully."}), 200

    except Exception as e:
        print(f"Error in /auth/login: {e}")
        return jsonify({"error": "Internal server error"}), 500


def forgot_password():
    try:
        db = get_db()
        data = request.get_json()
        token = data["token"]
        new_password = data["password"]
        print(data)
        try:
            check = jwt.decode(token, os.getenv("AUTH_SECRET"), algorithms=["HS256"])
            print(check)
        except Exception:
            return jsonify({"error": "Token expired."}), 400

        email = check["email"]
        # Fetch the user from the database
        user = db.query(users).filter(users.email == email).first()
        if not user:
            return jsonify({"error": "User not found."}), 404

        # Hash the new password
        hashed_new_password = bcrypt.hashpw(
            new_password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

        if user.password == hashed_new_password:
            return (
                jsonify(
                    {
                        "error": "You can't set new password same as your current password ! "
                    }
                ),
                403,
            )

        # Update the user's password in the database
        user.password = hashed_new_password
        db.commit()

        return jsonify({"message": "Password changed successfully."}), 200

    except Exception as e:
        print(f"Error in /auth/login: {e}")
        return jsonify({"error": "Internal server error"}), 500


def resendOtp():
    try:
        db = get_db()
        data = request.get_json()
        if not data or "ref_token" not in data:
            return jsonify({"error": "Something Went Wrong,try again later!."}), 400

        refresh_token = data["ref_token"]
        try:
            check = jwt.decode(
                refresh_token, os.getenv("REFRESH_TOKEN_SECRET"), algorithms=["HS256"]
            )
        except Exception:
            return (
                jsonify(
                    {
                        "error": (
                            "OTP session expired, try again filling "
                            "credentials and request OTP"
                        )
                    }
                ),
                400,
            )

        user = db.query(users).filter(users.email == check["email"]).first()
        if not user:
            return jsonify({"error": "User not found."}), 404

        token = jwt.encode(
            {
                "email": user.email,
                "exp": datetime.now(timezone.utc) + timedelta(seconds=330),
            },
            os.getenv("AUTH_SECRET"),
            algorithm="HS256",
        ).decode("utf-8")

        rtoken = jwt.encode(
            {
                "email": user.email,
                "exp": datetime.now(timezone.utc) + timedelta(minutes=20),
            },
            os.getenv("REFRESH_TOKEN_SECRET"),
            algorithm="HS256",
        ).decode("utf-8")

        # Generate a 6-digit OTP
        otp = random.randint(100000, 999999)

        # Convert OTP to string and append the token
        otp_with_token = f"{otp}-{token}"

        # Cleanup expired OTPs (older than 330 seconds)
        expiry_time = datetime.now(timezone.utc) - timedelta(seconds=330)
        db.query(OTP).filter(OTP.created_at < expiry_time).delete()

        # Check if an OTP entry already exists for this email and delete it
        existing_entry = db.query(OTP).filter(OTP.email == user.email).first()
        if existing_entry:
            db.delete(existing_entry)
            db.commit()

        # Create and save the new OTP entry with the modified OTP
        new_otp_entry = OTP(
            otp=otp_with_token, email=user.email, created_at=datetime.now(timezone.utc)
        )
        db.add(new_otp_entry)
        db.commit()

        # Send verification email (implement this function)
        send_verification_email(user.username, user.email, otp)

        # Respond with a success message and the token
        return (
            jsonify(
                {"message": "OTP sent successfully.", "token": token, "rtoken": rtoken}
            ),
            200,
        )

    except Exception:
        return jsonify({"error": "Internal server error"}), 500


async def githubCallback():
    try:
        data = request.get_json()
        code = data["code"]
        try:
            response = requests.post(
                "https://github.com/login/oauth/access_token",
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                json={
                    "client_id": os.getenv("GITHUB_CLIENT_ID"),
                    "client_secret": os.getenv("GITHUB_CLIENT_SECRET"),
                    "code": code,
                },
                timeout=10,  # 10 seconds timeout
            )
        except Exception:
            return jsonify({"error": "Internal server error"}), 500
        token_data = response.json()
        access_token = token_data.get("access_token")
        user = requests.get(
            "https://api.github.com/user",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": f"Bearer {access_token}",
            },
            timeout=10,  # 10 seconds timeout
        ).json()

        email = user["email"]
        username = user["login"]
        authId = str(user["id"])

        # Validate required fields
        if not all([email, username, authId]):
            return jsonify({"error": "Missing required fields."}), 400
        db = get_db()
        # Check if the user already exists using email
        existing_user = db.query(users).filter(users.email == email).first()

        if not existing_user:
            try:
                user = await create_user([email, username, authId])
            except Exception as e:
                print(e)
                return jsonify({"error": "Internal server error"}), 500
        else:
            user = existing_user
        db = get_db()

        # Generate a unique token from email ID with 1-sec expiration
        token = jwt.encode(
            {
                "email": user.email,
                "exp": datetime.now(timezone.utc) + timedelta(seconds=330),
            },
            os.getenv("AUTH_SECRET"),
            algorithm="HS256",
        ).decode("utf-8")

        rtoken = jwt.encode(
            {
                "email": user.email,
                "exp": datetime.now(timezone.utc) + timedelta(minutes=20),
            },
            os.getenv("REFRESH_TOKEN_SECRET"),
            algorithm="HS256",
        ).decode("utf-8")

        # Generate a 6-digit OTP
        otp = random.randint(100000, 999999)

        # Convert OTP to string and append the token
        otp_with_token = f"{otp}-{token}"

        # Cleanup expired OTPs (older than 330 seconds)
        expiry_time = datetime.now(timezone.utc) - timedelta(seconds=330)
        db.query(OTP).filter(OTP.created_at < expiry_time).delete()

        # Check if an OTP entry already exists for this email and delete it
        existing_entry = db.query(OTP).filter(OTP.email == user.email).first()
        if existing_entry:
            db.delete(existing_entry)
            db.commit()

        # Create and save the new OTP entry with the modified OTP
        new_otp_entry = OTP(
            otp=otp_with_token, email=user.email, created_at=datetime.now(timezone.utc)
        )
        db.add(new_otp_entry)
        db.commit()

        # Send verification email (implement this function)
        send_verification_email(user.username, user.email, otp)

        # Respond with a success message and the token
        return (
            jsonify(
                {"message": "OTP sent successfully.", "token": token, "rtoken": rtoken}
            ),
            200,
        )

    except Exception as e:
        print(e)
        return jsonify({"error": "Internal server error"}), 500


def get_user_profile():
    try:
        db = get_db()
        user = db.query(users).filter().first()
        if not user:
            return jsonify({"error": "User not found"}), 404
        return (
            jsonify(
                {
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                    }
                }
            ),
            200,
        )
    except Exception:
        return jsonify({"error": "Internal server error"}), 500


def change_password():
    try:
        # Get the Authorization header and check for token
        auth_header = request.headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Authorization token missing or invalid"}), 401

        token = auth_header.split(" ")[1]

        # Decode the token
        try:
            jwt.decode(token, os.getenv("AUTH_SECRET"), algorithms="HS256")
            g.token = token
        except Exception:
            return jsonify({"error": "Token expired or invalid"}), 400

        # Get the database connection
        db = get_db()
        data = request.get_json()

        # Check for required fields in the request body
        if not data or "current_password" not in data or "new_password" not in data:
            return jsonify({"error": "Missing required fields."}), 400

        current_password = data["current_password"]
        new_password = data["new_password"]

        # Decode token to get the user ID
        check = jwt.decode(g.token, os.getenv("AUTH_SECRET"), algorithms="HS256")
        user_id = check["userId"]

        # Fetch the user from the database using the user ID
        user = db.query(users).filter(users.id == str(user_id)).first()
        if not user:
            return jsonify({"error": "User not found."}), 404

        # Verify the current password
        if not bcrypt.checkpw(
            current_password.encode("utf-8"), user.password.encode("utf-8")
        ):
            return jsonify({"error": "Current password is incorrect."}), 401

        # Hash the new password
        hashed_new_password = bcrypt.hashpw(
            new_password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

        # Generate a new token with the hashed new password
        token = jwt.encode(
            {
                "pass": hashed_new_password,
                "exp": datetime.now(timezone.utc) + timedelta(seconds=330),
            },
            os.getenv("AUTH_SECRET"),
            algorithm="HS256",
        ).decode("utf-8")
        rtoken = jwt.encode(
            {
                "pass": hashed_new_password,
                "exp": datetime.now(timezone.utc) + timedelta(minutes=20),
            },
            os.getenv("REFRESH_TOKEN_SECRET"),
            algorithm="HS256",
        ).decode("utf-8")

        # Ensure the token is a string (if using older versions of PyJWT)
        if isinstance(token, bytes):
            token = token.decode("utf-8")

        # Generate a 6-digit OTP
        otp = random.randint(100000, 999999)

        # Concatenate OTP with the token
        otp_with_token = f"{otp}-{token}"

        # Cleanup expired OTPs older than 330 seconds
        expiry_time = datetime.now(timezone.utc) - timedelta(seconds=330)
        db.query(OTP).filter(OTP.created_at < expiry_time).delete()

        # Check if an OTP entry already exists for this user and delete it
        existing_entry = db.query(OTP).filter(OTP.email == user.email).first()
        if existing_entry:
            db.delete(existing_entry)
            db.commit()

        # Create and save the new OTP entry
        new_otp_entry = OTP(
            otp=otp_with_token, email=user.email, created_at=datetime.now(timezone.utc)
        )
        db.add(new_otp_entry)
        db.commit()

        # Send verification email (implement this function)
        send_verification_email(user.username, user.email, otp)

        # Respond with success message and the token
        return (
            jsonify(
                {"message": "OTP sent successfully.", "token": token, "rtoken": rtoken}
            ),
            200,
        )

    except Exception as e:
        print(f"Error in /auth/change-password: {e}")
        return jsonify({"error": "Internal server error"}), 500


def verifyChangeOtp():
    try:
        # Get the Authorization header and check for token
        auth_header = request.headers.get("authorization")
        print(auth_header)
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Authorization token missing or invalid"}), 401

        token = auth_header.split(" ")[1]

        # Decode the token
        try:
            jwt.decode(token, os.getenv("AUTH_SECRET"), algorithms="HS256")
            g.token = token
        except Exception:
            return jsonify({"error": "Token expired or invalid"}), 400
        db = get_db()
        data = request.get_json()
        print(data)

        # Check if OTP and token are provided
        if not data or "otp" not in data or "rtoken" not in data:
            return jsonify({"error": "Please provide both OTP and token."}), 400

        otp_received = data["otp"]
        token_received = data["rtoken"]

        # Check if the token is a valid 6-digit number
        if not 100000 <= int(otp_received) <= 999999:
            return jsonify({"error": "Invalid OTP."}), 400

        # Convert OTP to string and append the token
        otp_with_token = f"{otp_received}-{token_received}"

        # Verify if the OTP exists in the database
        otp_entry = db.query(OTP).filter(OTP.otp == otp_with_token).first()
        if not otp_entry:
            return jsonify({"error": "Invalid OTP."}), 400

        # Check if the OTP is expired
        current_time = datetime.now(
            timezone.utc
        )  # Get the current time in UTC with timezone

        # Ensure otp_creation_time is timezone-aware
        otp_creation_time = otp_entry.created_at
        if otp_creation_time.tzinfo is None:  # If it's naive, make it aware
            otp_creation_time = otp_creation_time.replace(tzinfo=timezone.utc)

        # Check if the current time is more than 330 seconds
        time_difference = current_time - otp_creation_time
        if time_difference.total_seconds() > 330:
            db.delete(otp_entry)
            db.commit()
            return jsonify({"error": "OTP expired."}), 400
        # Extract email from the OTP entry
        email = otp_entry.email
        # Delete the OTP entry after successful verification
        db.delete(otp_entry)
        db.commit()
        # Retrieve the user associated with the email
        user = db.query(users).filter(users.email == email).first()
        if not user:
            return jsonify({"error": "User not found."}), 404

        try:
            check = jwt.decode(
                token_received, os.getenv("AUTH_SECRET"), algorithms=["HS256"]
            )
        except Exception:
            return jsonify({"error": "Otp expired."}), 400

        new_hashed_password = check["pass"]
        # Update the user's password in the database
        user.password = new_hashed_password
        db.commit()

        return jsonify({"message": "Password changed successfully."}), 200

    except Exception as e:
        print(f"Error in /auth/otp: {e}")
        return jsonify({"error": "Internal server error"}), 500


def resendChangeOtp():
    try:

        # Get the Authorization header and check for token
        auth_header = request.headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Authorization token missing or invalid"}), 401

        token = auth_header.split(" ")[1]

        # Decode the token
        try:
            jwt.decode(token, os.getenv("AUTH_SECRET"), algorithms="HS256")
            g.token = token
        except Exception:
            return jsonify({"error": "Token expired or invalid"}), 400
        # db connection
        db = get_db()
        data = request.get_json()
        if not data or "ref_token" not in data:
            return jsonify({"error": "Something Went Wrong , try again later!."}), 400

        refresh_token = data["ref_token"]
        try:
            check = jwt.decode(
                refresh_token, os.getenv("REFRESH_TOKEN_SECRET"), algorithms=["HS256"]
            )
        except Exception:
            return (
                jsonify(
                    {
                        "error": (
                            "OTP session expired, try again filling "
                            + "credentials and request OTP"
                        )
                    }
                ),
                400,
            )

        decoded_token = jwt.decode(token, os.getenv("AUTH_SECRET"), algorithms="HS256")
        user_id = decoded_token["userId"]

        user = db.query(users).filter(users.id == user_id).first()
        if not user:
            return jsonify({"error": "User not found."}), 404

        # Generate a unique token from email ID with 1-sec expiration
        token = jwt.encode(
            {
                "pass": check["pass"],
                "exp": datetime.now(timezone.utc) + timedelta(seconds=330),
            },
            os.getenv("AUTH_SECRET"),
            algorithm="HS256",
        ).decode("utf-8")

        rtoken = jwt.encode(
            {
                "pass": check["pass"],
                "exp": datetime.now(timezone.utc) + timedelta(minutes=20),
            },
            os.getenv("REFRESH_TOKEN_SECRET"),
            algorithm="HS256",
        ).decode("utf-8")

        # Generate a 6-digit OTP
        otp = random.randint(100000, 999999)

        # Convert OTP to string and append the token
        otp_with_token = f"{otp}-{token}"

        # Cleanup expired OTPs (older than 330 seconds)
        expiry_time = datetime.now(timezone.utc) - timedelta(seconds=330)
        db.query(OTP).filter(OTP.created_at < expiry_time).delete()

        # Check if an OTP entry already exists for this email and delete it
        existing_entry = db.query(OTP).filter(OTP.email == user.email).first()
        if existing_entry:
            db.delete(existing_entry)
            db.commit()

        # Create and save the new OTP entry with the modified OTP
        new_otp_entry = OTP(
            otp=otp_with_token, email=user.email, created_at=datetime.now(timezone.utc)
        )
        db.add(new_otp_entry)
        db.commit()

        # Send verification email (implement this function)
        send_verification_email(user.username, user.email, otp)

        # Respond with a success message and the token
        return (
            jsonify(
                {"message": "OTP sent successfully.", "token": token, "rtoken": rtoken}
            ),
            200,
        )

    except Exception:
        return jsonify({"error": "Internal server error"}), 500
