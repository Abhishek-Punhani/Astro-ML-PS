import os
import random
import json
from datetime import datetime, timezone, timedelta
from flask import jsonify, request, make_response
import requests
from sqlalchemy.exc import IntegrityError
from sqlalchemy.exc import SQLAlchemyError
import bcrypt
import jwt
from db import get_auth_db, get_otp_db, get_data_db
from models.user import User as users
from models.otp import OTP
from models.peakResult import PeakResult
from emails.verification import send_verification_email
from emails.forgotpass import send_reset_password_email
from utils.validation import create_user
from utils.dict import peak_result_to_dict, user_to_dict
from config_redis import redis_client, data_redis_client


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
        if isinstance(new_user, dict) and "error" in new_user:
            return jsonify({"error": new_user["error"]}), 500

        token = jwt.encode(
            {
                "email": new_user["email"],
                "exp": datetime.now(timezone.utc) + timedelta(seconds=330),
            },
            os.getenv("AUTH_SECRET"),
            algorithm="HS256",
        )

        rtoken = jwt.encode(
            {
                "email": new_user["email"],
                "exp": datetime.now(timezone.utc) + timedelta(minutes=20),
            },
            os.getenv("REFRESH_TOKEN_SECRET"),
            algorithm="HS256",
        )

        # Generate a 6-digit OTP
        otp = random.randint(100000, 999999)

        # Convert OTP to string and append the token
        otp_with_token = f"{otp}-{token}"

        # Cleanup expired OTPs (older than 330 seconds)
        expiry_time = datetime.now(timezone.utc) - timedelta(seconds=330)
        otp_db.query(OTP).filter(OTP.created_at < expiry_time).delete()

        # Check if an OTP entry already exists for this email and delete it
        existing_entry = (
            otp_db.query(OTP).filter(OTP.email == new_user["email"]).first()
        )
        if existing_entry:
            otp_db.delete(existing_entry)
            otp_db.commit()

        # Create and save the new OTP entry with the modified OTP
        new_otp_entry = OTP(
            otp=otp_with_token,
            email=new_user["email"],
            created_at=datetime.now(timezone.utc),
        )
        otp_db.add(new_otp_entry)
        otp_db.commit()

        # Send verification email (implement this function)
        send_verification_email(new_user["username"], new_user["email"], otp)

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
        auth_db = get_auth_db()
        data = request.get_json()
        if not data or "email" not in data or "password" not in data:
            return jsonify({"error": "Missing required fields."}), 400
        email = data["email"]
        password = data["password"]

        # Cache key for the user based on email
        cache_key = f"user:{email}"

        # Check if user data exists in Redis cache
        cached_user = redis_client.get(cache_key)

        if cached_user is not None:
            user = json.loads(cached_user)
        else:

            try:
                user = auth_db.query(users).filter(users.email == email).first()
                if user is None:
                    return (
                        jsonify(
                            {
                                "error": "User Dosnt exist Please register yourself or sign in via Google or Github"
                            }
                        ),
                        401,
                    )
                user = user_to_dict(user)
                redis_client.setex(cache_key, 84000, json.dumps(user))
            except SQLAlchemyError as e:
                print("Database error occurred:", e)
                return jsonify({"error": "An error occurred. Please try again."}), 500
            finally:
                auth_db.close()

        if not user or not bcrypt.checkpw(
            password.encode("utf-8"), user["password"].encode("utf-8")
        ):
            return jsonify({"error": "Invalid credentials"}), 401
        # Generate a unique token from email ID with 1-sec expiration
        token = jwt.encode(
            {
                "email": user["email"],
                "exp": datetime.now(timezone.utc) + timedelta(seconds=330),
            },
            os.getenv("AUTH_SECRET"),
            algorithm="HS256",
        )

        rtoken = jwt.encode(
            {
                "email": user["email"],
                "exp": datetime.now(timezone.utc) + timedelta(minutes=20),
            },
            os.getenv("REFRESH_TOKEN_SECRET"),
            algorithm="HS256",
        )

        # Generate a 6-digit OTP
        otp = random.randint(100000, 999999)

        # Convert OTP to string and append the token
        otp_with_token = f"{otp}-{token}"

        # Cleanup expired OTPs (older than 330 seconds)
        expiry_time = datetime.now(timezone.utc) - timedelta(seconds=330)
        otp_db.query(OTP).filter(OTP.created_at < expiry_time).delete()

        # Check if an OTP entry already exists for this email and delete it
        existing_entry = otp_db.query(OTP).filter(OTP.email == user["email"]).first()
        if existing_entry:
            otp_db.delete(existing_entry)
            otp_db.commit()

        # Create and save the new OTP entry with the modified OTP
        new_otp_entry = OTP(
            otp=otp_with_token,
            email=user["email"],
            created_at=datetime.now(timezone.utc),
        )
        otp_db.add(new_otp_entry)
        otp_db.commit()

        # Send verification email (implement this function)
        send_verification_email(user["username"], user["email"], otp)

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
        )

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
        auth_db = get_auth_db()
        data = request.get_json()

        # Extracting necessary parameters from the request body
        email = data.get("email")
        username = data.get("username")
        authId = data.get("authId")

        # Validate required fields
        if not all([email, username, authId]):
            return jsonify({"error": "Missing required fields."}), 400

        # Cache key for the user based on email
        cache_key = f"user:{email}"

        # Check if user data exists in Redis cache
        cached_user = redis_client.get(cache_key)
        if cached_user is not None:
            existing_user = json.loads(cached_user)
        else:
            # Check if the user already exists using email
            existing_user = auth_db.query(users).filter(users.email == email).first()
            if existing_user is not None:
                existing_user = user_to_dict(existing_user)
                redis_client.setex(cache_key, 84000, json.dumps(existing_user))

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
                "email": user["email"],
                "exp": datetime.now(timezone.utc) + timedelta(seconds=330),
            },
            os.getenv("AUTH_SECRET"),
            algorithm="HS256",
        )

        rtoken = jwt.encode(
            {
                "email": user["email"],
                "exp": datetime.now(timezone.utc) + timedelta(minutes=20),
            },
            os.getenv("REFRESH_TOKEN_SECRET"),
            algorithm="HS256",
        )

        # Generate a 6-digit OTP
        otp = random.randint(100000, 999999)

        # Convert OTP to string and append the token
        otp_with_token = f"{otp}-{token}"

        # Cleanup expired OTPs (older than 330 seconds)
        expiry_time = datetime.now(timezone.utc) - timedelta(seconds=330)
        otp_db.query(OTP).filter(OTP.created_at < expiry_time).delete()

        # Check if an OTP entry already exists for this email and delete it
        existing_entry = otp_db.query(OTP).filter(OTP.email == user["email"]).first()
        if existing_entry:
            otp_db.delete(existing_entry)
            otp_db.commit()

        # Create and save the new OTP entry with the modified OTP
        new_otp_entry = OTP(
            otp=otp_with_token,
            email=user["email"],
            created_at=datetime.now(timezone.utc),
        )
        otp_db.add(new_otp_entry)
        otp_db.commit()

        # Send verification email (implement this function)
        send_verification_email(user["username"], user["email"], otp)

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
        auth_db = get_auth_db()
        data_db = get_data_db()
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

        # Cache key for the user based on email
        cache_key = f"user:{email}"

        # Check if user data exists in Redis cache
        cached_user = redis_client.get(cache_key)

        if cached_user is not None:
            user = json.loads(cached_user)
        else:
            # Retrieve the user associated with the email
            user = auth_db.query(users).filter(users.email == email).first()
            if not user:
                return jsonify({"error": "User not found."}), 404
            user = user_to_dict(user)
            redis_client.setex(cache_key, 84000, json.dumps(user))

        # Cache key for peak results
        user_id = user["id"]
        peak_results_cache_key = f"peak_results:{user_id}"

        # Check if peak results exist in Redis cache
        cached_peak_results = data_redis_client.get(peak_results_cache_key)

        if cached_peak_results is not None:
            peak_results = json.loads(cached_peak_results)
        else:
            # Retrieve PeakResult objects for the user's peak_result_ids
            peak_results = (
                data_db.query(PeakResult)
                .filter(PeakResult.id.in_(user["peak_result_ids"]))
                .all()
            )
            # Convert PeakResult objects to dictionaries
            peak_results = [peak_result_to_dict(result) for result in peak_results]
            # Cache the peak results
            data_redis_client.setex(
                peak_results_cache_key, 84000, json.dumps(peak_results)
            )

        # Generate project names as an array of objects with id and project_name
        project_names = [
            {"id": str(result["id"]), "project_name": result["project_name"]}
            for result in peak_results
        ]

        # Generate JWT tokens
        access_token = jwt.encode(
            {"userId": str(user["id"])}, os.getenv("AUTH_SECRET"), algorithm="HS256"
        )
        refresh_token = jwt.encode(
            {"userId": str(user["id"])},
            os.getenv("REFRESH_TOKEN_SECRET"),
            algorithm="HS256",
        )

        # Decode tokens to strings
        access_token_str = (
            access_token if isinstance(access_token, str) else access_token
        )
        refresh_token_str = (
            refresh_token if isinstance(refresh_token, str) else refresh_token
        )

        # Response Structure
        response_data = {
            "message": "Login success.",
            "user": {
                "id": str(user["id"]),
                "username": user["username"],
                "email": user["email"],
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
        if not email:
            return jsonify({"error": "Missing Fields"}), 500
        # Check for user credentials
        # Cache key for the user based on email
        cache_key = f"user:{email}"

        # Check if user data exists in Redis cache
        cached_user = redis_client.get(cache_key)

        if cached_user is not None:
            user = json.loads(cached_user)
        else:
            user = auth_db.query(users).filter(users.email == email).first()
            if user is not None:
                user = user_to_dict(user)
                redis_client.setex(cache_key, 84000, json.dumps(user))
            else:
                return jsonify({"error": "User Not Found!"}), 500
        if not user:
            return jsonify({"error": "Invalid credentials"}), 401

        # Generate a unique token from email ID with 1-sec expiration
        token = jwt.encode(
            {
                "email": user["email"],
                "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
            },
            os.getenv("AUTH_SECRET"),
            algorithm="HS256",
        )
        clientapi = os.getenv("CLIENT_URI")
        link = clientapi + "/auth/newcredentials/" + str(user["id"]) + "/" + token
        send_reset_password_email(user["username"], user["email"], link)
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
        if not token and new_password:
            return jsonify({"error": "Missing Fields."}), 400
        try:
            check = jwt.decode(token, os.getenv("AUTH_SECRET"), algorithms=["HS256"])
            print(check)
        except Exception:
            return jsonify({"error": "Token expired."}), 400

        email = check["email"]
        # Fetch the user from the database
        # Cache key for the user based on email
        cache_key = f"user:{email}"

        # Check if user data exists in Redis cache
        cached_user = redis_client.get(cache_key)

        if cached_user is not None:
            user = json.loads(cached_user)
        else:
            user = auth_db.query(users).filter(users.email == email).first()
            if user is not None:
                user = user_to_dict(user)
                redis_client.setex(cache_key, 84000, json.dumps(user))
            else:
                return jsonify({"error": "User Not Found!"}), 500
        if not user:
            return jsonify({"error": "User not found."}), 404

        # Hash the new password
        hashed_new_password = bcrypt.hashpw(
            new_password.encode("utf-8"), bcrypt.gensalt()
        )

        if user["password"] == hashed_new_password:
            return (
                jsonify(
                    {
                        "error": "You can't set new password same as your current password ! "
                    }
                ),
                403,
            )

        # Update the user's password in the database
        user["password"] = hashed_new_password
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
        otp_db = get_otp_db()
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
        email = check["email"]
        # Cache key for the user based on email
        cache_key = f"user:{email}"

        # Check if user data exists in Redis cache
        cached_user = redis_client.get(cache_key)

        if cached_user is not None:
            user = json.loads(cached_user)
        else:
            user = auth_db.query(users).filter(users.email == email).first()
            if user is not None:
                user = user_to_dict(user)
                redis_client.setex(cache_key, 84000, json.dumps(user))
            else:
                return jsonify({"error": "User Not Found!"}), 500
        if not user:
            return jsonify({"error": "User not found."}), 404

        token = jwt.encode(
            {
                "email": user["email"],
                "exp": datetime.now(timezone.utc) + timedelta(seconds=330),
            },
            os.getenv("AUTH_SECRET"),
            algorithm="HS256",
        )

        rtoken = jwt.encode(
            {
                "email": user["email"],
                "exp": datetime.now(timezone.utc) + timedelta(minutes=20),
            },
            os.getenv("REFRESH_TOKEN_SECRET"),
            algorithm="HS256",
        )

        # Generate a 6-digit OTP
        otp = random.randint(100000, 999999)

        # Convert OTP to string and append the token
        otp_with_token = f"{otp}-{token}"

        # Cleanup expired OTPs (older than 330 seconds)
        expiry_time = datetime.now(timezone.utc) - timedelta(seconds=330)
        otp_db.query(OTP).filter(OTP.created_at < expiry_time).delete()

        # Check if an OTP entry already exists for this email and delete it
        existing_entry = otp_db.query(OTP).filter(OTP.email == user["email"]).first()
        if existing_entry:
            otp_db.delete(existing_entry)
            otp_db.commit()

        # Create and save the new OTP entry with the modified OTP
        new_otp_entry = OTP(
            otp=otp_with_token,
            email=user["email"],
            created_at=datetime.now(timezone.utc),
        )
        otp_db.add(new_otp_entry)
        otp_db.commit()

        # Send verification email (implement this function)
        send_verification_email(user["username"], user["email"], otp)

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
        # Cache key for the user based on email
        cache_key = f"user:{email}"

        # Check if user data exists in Redis cache
        cached_user = redis_client.get(cache_key)
        if cached_user is not None:
            existing_user = json.loads(cached_user)
        else:
            # Check if the user already exists using email
            existing_user = auth_db.query(users).filter(users.email == email).first()
            if existing_user is not None:
                existing_user = user_to_dict(existing_user)
                redis_client.setex(cache_key, 84000, json.dumps(existing_user))

        if not existing_user:
            try:
                user = await create_user({"email": email, "username": username, "authId": authId})
            except Exception as e:
                print(e)
                return jsonify({"error": "Internal server error"}), 500
        else:
            user = existing_user

        otp_db = get_otp_db()

        # Generate a unique token from email ID with 1-sec expiration
        token = jwt.encode(
            {
                "email": user["email"],
                "exp": datetime.now(timezone.utc) + timedelta(seconds=330),
            },
            os.getenv("AUTH_SECRET"),
            algorithm="HS256",
        )

        rtoken = jwt.encode(
            {
                "email": user["email"],
                "exp": datetime.now(timezone.utc) + timedelta(minutes=20),
            },
            os.getenv("REFRESH_TOKEN_SECRET"),
            algorithm="HS256",
        )

        # Generate a 6-digit OTP
        otp = random.randint(100000, 999999)

        # Convert OTP to string and append the token
        otp_with_token = f"{otp}-{token}"

        # Cleanup expired OTPs (older than 330 seconds)
        expiry_time = datetime.now(timezone.utc) - timedelta(seconds=330)
        otp_db.query(OTP).filter(OTP.created_at < expiry_time).delete()

        # Check if an OTP entry already exists for this email and delete it
        existing_entry = otp_db.query(OTP).filter(OTP.email == user["email"]).first()
        if existing_entry:
            otp_db.delete(existing_entry)
            otp_db.commit()

        # Create and save the new OTP entry with the modified OTP
        new_otp_entry = OTP(
            otp=otp_with_token,
            email=user["email"],
            created_at=datetime.now(timezone.utc),
        )
        otp_db.add(new_otp_entry)
        otp_db.commit()

        # Send verification email (implement this function)
        send_verification_email(user["username"], user["email"], otp)

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
