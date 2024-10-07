import os
import random
from datetime import datetime, timezone, timedelta
from flask import jsonify, request, make_response
import requests
from sqlalchemy.exc import IntegrityError
from sqlalchemy.exc import SQLAlchemyError
import bcrypt
import jwt
from db import get_auth_db,get_otp_db,get_data_db
from models.user import User as users
from models.otp import OTP
from models.peakResult import PeakResult
from emails.verification import send_verification_email
from emails.forgotpass import send_reset_password_email
from utils.validation import create_user




async def register():
    try:
        otp_db = get_otp_db()
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
        otp_db.query(OTP).filter(OTP.created_at < expiry_time).delete()

        # Check if an OTP entry already exists for this email and delete it
        existing_entry = otp_db.query(OTP).filter(OTP.email == new_user.email).first()
        if existing_entry:
            otp_db.delete(existing_entry)
            otp_db.commit()

        # Create and save the new OTP entry with the modified OTP
        new_otp_entry = OTP(
            otp=otp_with_token,
            email=new_user.email,
            created_at=datetime.now(timezone.utc),
        )
        otp_db.add(new_otp_entry)
        otp_db.commit()

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
        otp_db.rollback()
        return jsonify({"error": "An error occurred. Please try again."}), 500
    except Exception as e:
        print(f"Error in /auth/register: {e}")
        return jsonify({"error": "Internal server error"}), 500
    finally:
        otp_db.close()


def login():
    try:
        otp_db = get_otp_db()
        auth_db=get_auth_db()
        data = request.get_json()
        if not data or "email" not in data or "password" not in data:
            return jsonify({"error": "Missing required fields."}), 400
        email = data["email"]
        password = data["password"]

        # Check for user credentials
        try:
            user = auth_db.query(users).filter(users.email == email).first()
        except SQLAlchemyError as e:
            print("Database error occurred:", e)
            return jsonify({"error": "An error occurred. Please try again."}), 500
        finally:
            auth_db.close()
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
        otp_db.query(OTP).filter(OTP.created_at < expiry_time).delete()

        # Check if an OTP entry already exists for this email and delete it
        existing_entry = otp_db.query(OTP).filter(OTP.email == user.email).first()
        if existing_entry:
            otp_db.delete(existing_entry)
            otp_db.commit()

        # Create and save the new OTP entry with the modified OTP
        new_otp_entry = OTP(
            otp=otp_with_token, email=user.email, created_at=datetime.now(timezone.utc)
        )
        otp_db.add(new_otp_entry)
        otp_db.commit()

        # Send verification email (implement this function)
        send_verification_email(user.username, user.email, otp)

        # Respond with a success message and the token
        return (
            jsonify(
                {
                    "message": "OTP sent successfully.",
                    "token": token,
                    "rtoken": rtoken,
                }
            ),
            200,
        )
    except IntegrityError:
        otp_db.rollback()
        auth_db.rollback()
        return jsonify({"error": "An error occurred. Please try again."}), 500
    except Exception as e:
        print(f"Error in /auth/login: {e}")
        return jsonify({"error": "Internal server error"}), 500
    finally:
        otp_db.close()
        auth_db.close()


def refresh_token():
    try:
        auth_db = get_auth_db()
        refresh_token_cookie = request.cookies.get("xfd")
        if not refresh_token_cookie:
            return jsonify({"error": "Please login."}), 401

        check = jwt.decode(
            refresh_token_cookie,
            os.getenv("REFRESH_TOKEN_SECRET"),
            algorithms=["HS256"],
        )
        user = auth_db.query(users).filter(users.id == check["userId"]).first()
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
    except IntegrityError:
        auth_db.rollback()
        return jsonify({"error": "An error occurred. Please try again."}), 500
    except Exception as e:
        print(f"Error in /auth/refreshtoken: {e}")
        return jsonify({"error": "Internal server error"}), 500
    finally:
        auth_db.close()

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
        otp_db = get_otp_db()
        auth_db=get_auth_db()
        data = request.get_json()

        # Extracting necessary parameters from the request body
        email = data.get("email")
        username = data.get("username")
        authId = data.get("authId")

        # Validate required fields
        if not all([email, username, authId]):
            return jsonify({"error": "Missing required fields."}), 400

        # Check if the user already exists using email
        existing_user = auth_db.query(users).filter(users.email == email).first()

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
        otp_db.query(OTP).filter(OTP.created_at < expiry_time).delete()

        # Check if an OTP entry already exists for this email and delete it
        existing_entry = otp_db.query(OTP).filter(OTP.email == user.email).first()
        if existing_entry:
            otp_db.delete(existing_entry)
            otp_db.commit()

        # Create and save the new OTP entry with the modified OTP
        new_otp_entry = OTP(
            otp=otp_with_token, email=user.email, created_at=datetime.now(timezone.utc)
        )
        otp_db.add(new_otp_entry)
        otp_db.commit()

        # Send verification email (implement this function)
        send_verification_email(user.username, user.email, otp)

        # Respond with a success message and the token
        return (
            jsonify(
                {"message": "OTP sent successfully.", "token": token, "rtoken": rtoken}
            ),
            200,
        )

    except IntegrityError:
        otp_db.rollback()
        auth_db.rollback()
        return jsonify({"error": "An error occurred. Please try again."}), 500
    except Exception as e:
        print(f"Error in /auth/googlelogin: {e}")
        return jsonify({"error": "Internal server error"}), 500
    finally:
        otp_db.close()
        auth_db.close()


def verifyOtp():
    try:
        otp_db = get_otp_db()
        auth_db=get_auth_db()
        data_db=get_data_db()
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
        otp_entry = otp_db.query(OTP).filter(OTP.otp == otp_with_token).first()
        if not otp_entry:
            return jsonify({"error": "Invalid OTP."}), 400

        # Check if the OTP is expired
        current_time = datetime.now(timezone.utc)
        otp_creation_time = otp_entry.created_at

        if otp_creation_time.tzinfo is None:
            otp_creation_time = otp_creation_time.replace(tzinfo=timezone.utc)

        time_difference = current_time - otp_creation_time
        if time_difference.total_seconds() > 330:
            otp_db.delete(otp_entry)
            otp_db.commit()
            return jsonify({"error": "OTP expired."}), 400

        try:
            jwt.decode(token_received, os.getenv("AUTH_SECRET"), algorithms=["HS256"])
        except Exception:
            return jsonify({"error": "Token expired."}), 400

        # Extract email from the OTP entry
        email = otp_entry.email

        # Delete the OTP entry after successful verification
        otp_db.delete(otp_entry)
        otp_db.commit()

        # Retrieve the user associated with the email
        user = auth_db.query(users).filter(users.email == email).first()
        if not user:
            return jsonify({"error": "User not found."}), 404

        print(user.peak_result_ids)

        # Retrieve PeakResult objects for the user's peak_result_ids
        peak_results = data_db.query(PeakResult).filter(PeakResult.id.in_(user.peak_result_ids)).all()
        
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

    except IntegrityError:
        otp_db.rollback()
        auth_db.rollback()
        data_db.rollback()
        return jsonify({"error": "An error occurred. Please try again."}), 500
    except Exception as e:
        print(f"Error in /auth/verifyotp: {e}")
        return jsonify({"error": "Internal server error"}), 500
    finally:
        otp_db.close()
        data_db.close()
        data_db.close()


def sendOtp():
    try:
        auth_db = get_auth_db()
        data = request.get_json()
        email = data["email"]

        # Check for user credentials
        user = auth_db.query(users).filter(users.email == email).first()
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
    
    except IntegrityError:
        auth_db.rollback()
        return jsonify({"error": "An error occurred. Please try again."}), 500

    except Exception as e:
        print(f"Error in /auth/login: {e}")
        return jsonify({"error": "Internal server error"}), 500
    
    finally:
        auth_db.close()


def forgot_password():
    try:
        auth_db = get_auth_db()
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
        user = auth_db.query(users).filter(users.email == email).first()
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
        auth_db.commit()
        return jsonify({"message": "Password changed successfully."}), 200
    
    except IntegrityError:
        auth_db.rollback()
        return jsonify({"error": "An error occurred. Please try again."}), 500

    except Exception as e:
        print(f"Error in /auth/login: {e}")
        return jsonify({"error": "Internal server error"}), 500
    
    finally:
        auth_db.close()


def resendOtp():
    try:
        auth_db = get_auth_db()
        otp_db=get_otp_db()
        data = request.get_json()
        print(data)
        if not data or "ref_token" not in data:
            print("error here")
            return jsonify({"error": "Something Went Wrong,try again later!."}), 400

        refresh_token = data["ref_token"]
        try:
            check = jwt.decode(
                refresh_token, os.getenv("REFRESH_TOKEN_SECRET"), algorithms=["HS256"]
            )
        except Exception as e:
            print(f"JWT decoding failed:{e}")
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

        user = auth_db.query(users).filter(users.email == check["email"]).first()
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
        otp_db.query(OTP).filter(OTP.created_at < expiry_time).delete()

        # Check if an OTP entry already exists for this email and delete it
        existing_entry = otp_db.query(OTP).filter(OTP.email == user.email).first()
        if existing_entry:
            otp_db.delete(existing_entry)
            otp_db.commit()

        # Create and save the new OTP entry with the modified OTP
        new_otp_entry = OTP(
            otp=otp_with_token, email=user.email, created_at=datetime.now(timezone.utc)
        )
        otp_db.add(new_otp_entry)
        otp_db.commit()

        # Send verification email (implement this function)
        send_verification_email(user.username, user.email, otp)

        # Respond with a success message and the token
        return (
            jsonify(
                {"message": "OTP sent successfully.", "token": token, "rtoken": rtoken}
            ),
            200,
        )

    except IntegrityError:
        auth_db.rollback()
        otp_db.rollback()
        return jsonify({"error": "An error occurred. Please try again."}), 500
    
    except Exception:
        return jsonify({"error": "Internal server error"}), 500
    finally:
        otp_db.close()
        auth_db.close()


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
        auth_db = get_auth_db()
        # Check if the user already exists using email
        existing_user = auth_db.query(users).filter(users.email == email).first()

        if not existing_user:
            try:
                user = await create_user([email, username, authId])
            except Exception as e:
                print(e)
                return jsonify({"error": "Internal server error"}), 500
        else:
            user = existing_user
        otp_db = get_otp_db()

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
        otp_db.query(OTP).filter(OTP.created_at < expiry_time).delete()

        # Check if an OTP entry already exists for this email and delete it
        existing_entry = otp_db.query(OTP).filter(OTP.email == user.email).first()
        if existing_entry:
            otp_db.delete(existing_entry)
            otp_db.commit()

        # Create and save the new OTP entry with the modified OTP
        new_otp_entry = OTP(
            otp=otp_with_token, email=user.email, created_at=datetime.now(timezone.utc)
        )
        otp_db.add(new_otp_entry)
        otp_db.commit()

        # Send verification email (implement this function)
        send_verification_email(user.username, user.email, otp)

        # Respond with a success message and the token
        return (
            jsonify(
                {"message": "OTP sent successfully.", "token": token, "rtoken": rtoken}
            ),
            200,
        )
    
    except IntegrityError:
        auth_db.rollback()
        otp_db.rollback()
        return jsonify({"error": "An error occurred. Please try again."}), 500

    except Exception as e:
        print(e)
        return jsonify({"error": "Internal server error"}), 500