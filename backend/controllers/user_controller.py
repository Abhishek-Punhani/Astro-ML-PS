import hashlib
import json
import os
import numpy as np
import random
from flask import jsonify, request, g
from sqlalchemy.exc import IntegrityError
from db import get_auth_db, get_otp_db, get_data_db
from models.peakResult import PeakResult
from models.user import User as users
from models.otp import OTP
import jwt
from model import returnable
from datetime import datetime, timezone, timedelta
from emails.verification import send_verification_email
from config_redis import data_redis_client, redis_client
from utils.dict import peak_result_to_dict
import bcrypt


def convert_numpy_to_native(data):
    """Recursively convert numpy types to native Python types."""
    if isinstance(data, dict):
        return {key: convert_numpy_to_native(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [convert_numpy_to_native(item) for item in data]
    elif isinstance(data, np.integer):  # Convert numpy int types
        return int(data)
    elif isinstance(data, np.floating):  # Convert numpy float types
        return float(data)
    elif isinstance(data, np.ndarray):  # Convert numpy arrays to lists
        return data.tolist()
    else:
        return data


def generate_data_hash(data_dict):
    # Convert all numpy types to Python native types
    native_data = convert_numpy_to_native(data_dict)
    # Convert dict to JSON string
    data_str = json.dumps(native_data, sort_keys=True)
    # Generate and return hash
    return hashlib.sha256(data_str.encode("utf-8")).hexdigest()


def convert_to_serializable(obj):
    if isinstance(obj, np.recarray):
        return [dict(zip(obj.dtype.names, row)) for row in obj]
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, np.generic):
        return obj.item()
    elif isinstance(obj, dict):
        return {k: convert_to_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_serializable(i) for i in obj]
    else:
        return obj


def change_password():
    otp_db = None
    auth_db = None
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
        auth_db = get_auth_db()
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
        user = auth_db.query(users).filter(users.id == str(user_id)).first()
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

        otp_db = get_otp_db()
        otp_db.query(OTP).filter(OTP.created_at < expiry_time).delete()

        # Check if an OTP entry already exists for this user and delete it
        existing_entry = otp_db.query(OTP).filter(OTP.email == user.email).first()
        if existing_entry:
            otp_db.delete(existing_entry)
            otp_db.commit()

        # Create and save the new OTP entry
        new_otp_entry = OTP(
            otp=otp_with_token, email=user.email, created_at=datetime.now(timezone.utc)
        )
        otp_db.add(new_otp_entry)
        otp_db.commit()

        # Send verification email (implement this function)
        send_verification_email(user.username, user.email, otp)

        # Respond with success message and the token
        return (
            jsonify(
                {"message": "OTP sent successfully.", "token": token, "rtoken": rtoken}
            ),
            200,
        )

    except IntegrityError:
        if auth_db:
            auth_db.rollback()
        if otp_db:
            otp_db.rollback()
        return jsonify({"error": "An error occurred. Please try again."}), 500

    except Exception as e:
        print(f"Error in /auth/change-password: {e}")
        return jsonify({"error": "Internal server error"}), 500

    finally:
        if otp_db:
            otp_db.close()
        if auth_db:
            auth_db.close()


def verifyOtp():
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
        data = request.get_json()

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

        otp_db = get_otp_db()
        # Verify if the OTP exists in the database
        otp_entry = otp_db.query(OTP).filter(OTP.otp == otp_with_token).first()
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
            otp_db.delete(otp_entry)
            otp_db.commit()
            return jsonify({"error": "OTP expired."}), 400
        # Extract email from the OTP entry
        email = otp_entry.email
        # Delete the OTP entry after successful verification
        otp_db.delete(otp_entry)
        otp_db.commit()
        # Retrieve the user associated with the email
        auth_db = get_auth_db()
        user = auth_db.query(users).filter(users.email == email).first()
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
        auth_db.commit()

        return jsonify({"message": "Password changed successfully."}), 200

    except IntegrityError:
        auth_db.rollback()
        otp_db.rollback()
        return jsonify({"error": "An error occurred. Please try again."}), 500

    except Exception as e:
        print(f"Error in /auth/otp: {e}")
        return jsonify({"error": "Internal server error"}), 500

    finally:
        auth_db.close()
        otp_db.close()


def resendOtp():
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
        auth_db = get_auth_db()
        user = auth_db.query(users).filter(users.id == user_id).first()
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

        otp_db = get_otp_db()
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


def analyze():
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
        data = request.get_json()

        # Check if 'data' key exists and is a list
        if "data" in data and isinstance(data["data"], list):
            req_data = data["data"]
            # print(req_data)
            # Ensure 'FRACEXP' is set to 0 if it's None for each entry
            for entry in req_data:
                if isinstance(entry, dict):  # Ensure each entry is a dictionary
                    if entry.get("FRACEXP") is None:
                        entry["FRACEXP"] = 0
                if isinstance(entry, dict):  # Ensure each entry is a dictionary
                    if entry.get("ERROR") is None:
                        entry["ERROR"] = 0

            # Define dtype for structured array
            dtype = np.dtype(
                [
                    ("TIME", "f8"),  # float64
                    ("RATE", "f8"),  # float64
                    ("ERROR", "f8"),  # float64
                    ("FRACEXP", "i4"),  # int32
                ]
            )

            # Create data tuples from req_data
            data_tuples = [
                (entry["TIME"], entry["RATE"], entry["ERROR"], entry["FRACEXP"])
                for entry in req_data
            ]

            # Convert to recarray
            rec_array = np.array(data_tuples, dtype=dtype).view(np.recarray)

            # Call the returnable function
            res = returnable(rec_array)
            res = convert_to_serializable(res)

            return jsonify({"res": res})

        else:
            return jsonify({"error": "Invalid input data format"}), 400

    except Exception as e:
        print(f"Exception: {e}")
        return jsonify({"error": "Internal server error"}), 500


def save():
    try:
        # Get the Authorization header and check for token
        auth_header = request.headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Authorization token missing or invalid"}), 401

        token = auth_header.split(" ")[1]

        # Decode the token
        try:
            check = jwt.decode(token, os.getenv("AUTH_SECRET"), algorithms="HS256")
            g.token = token
        except Exception:
            return jsonify({"error": "Token expired or invalid."}), 400

        data = request.get_json()["data"]
        required_keys = [
            "x",
            "y",
            "time_of_occurances",
            "time_corresponding_peak_flux",
            "max_peak_flux",
            "average_peak_flux",
            "rise_time",
            "left",
            "decay_time",
            "right",
            "prominences",
            "cluster_labels",
            "silhouette_avg",
            "projectName",
        ]

        # Check for missing keys in the data
        missing_keys = [key for key in required_keys if key not in data]
        if missing_keys:
            print(f"Missing keys: {missing_keys}")
            return (
                jsonify(
                    {"error": "Missing keys in data", "missing_keys": missing_keys}
                ),
                400,
            )

        check = jwt.decode(g.token, os.getenv("AUTH_SECRET"), algorithms="HS256")
        user_id = check["userId"]
        auth_db = get_auth_db()

        # Fetch the user from the database using the user ID
        user = auth_db.query(users).filter(users.id == str(user_id)).first()
        if not user:
            return jsonify({"error": "User not found."}), 404

        print(user)
        # Generate data hash
        data_hash = generate_data_hash(data)
        data_db = get_data_db()
        # Check if an existing result with the same data_hash exists

        existing_result = (
            data_db.query(PeakResult).filter(PeakResult.data_hash == data_hash).first()
        )

        # If an existing result is found, check if it's already in the user's peak_result_ids
        if existing_result:
            if existing_result.id in user.peak_result_ids:
                return (
                    jsonify(
                        {
                            "message": "Data already exists",
                            "data": existing_result.project_name,
                        }
                    ),
                    200,
                )

        # Create a new PeakResult object
        new_result = PeakResult(
            max_peak_flux=data["max_peak_flux"],
            average_peak_flux=data["average_peak_flux"],
            rise_time=data["rise_time"],
            decay_time=data["decay_time"],
            x=data["x"],
            y=data["y"],
            time_of_occurances=data["time_of_occurances"],
            time_corresponding_peak_flux=data["time_corresponding_peak_flux"],
            silhouette_score=data["silhouette_avg"],
            data_hash=data_hash,
            project_name=data["projectName"],
            right=data["right"],
            left=data["left"],
        )

        # Add the new result to the database
        data_db.add(new_result)
        data_db.commit()
        if new_result.id not in user.peak_result_ids:
            user.peak_result_ids.append(new_result.id)
            auth_db.commit()

        project_name = {"id": new_result.id, "project_name": new_result.project_name}

        redis_key = f"peak_result:{new_result.id}"
        data_redis_client.setex(
            redis_key, 86400, json.dumps(peak_result_to_dict(new_result))
        )

        cache_key = f"user:{user.email}"
        redis_client.delete(cache_key)
        peak_results_cache_key = f"peak_results:{user.id}"
        data_redis_client.delete(peak_results_cache_key)

        # Use a list comprehension to convert each peak result to a dictionary
        peak_results = (
            data_db.query(PeakResult)
            .filter(PeakResult.id.in_(user.peak_result_ids))
            .all()
        )
        new_peak_results = [peak_result_to_dict(result) for result in peak_results]
        # Cache the peak results
        data_redis_client.setex(
            peak_results_cache_key, 84000, json.dumps(new_peak_results)
        )
        return (
            jsonify(
                {"message": "Data saved successfully", "project_name": project_name}
            ),
            200,
        )

    except IntegrityError:
        auth_db.rollback()
        data_db.rollback()
        return jsonify({"error": "An error occurred. Please try again."}), 500

    except Exception as e:
        print(f"Exception: {e}")
        return jsonify({"error": "Internal server error."}), 500

    finally:
        data_db.close()
        auth_db.close()


def getData(id):
    data_db = None
    try:
        # Get the Authorization header and check for token
        auth_header = request.headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Authorization token missing or invalid"}), 401

        token = auth_header.split(" ")[1]

        # Decode the token
        try:
            jwt.decode(token, os.getenv("AUTH_SECRET"), algorithms=["HS256"])
            g.token = token
        except Exception:
            return jsonify({"error": "Token expired or invalid."}), 400

        if not id:
            return jsonify({"error": "Missing required fields."}), 400

        # Check Redis for cached data
        redis_key = f"peak_result:{id}"
        cached_result = data_redis_client.get(redis_key)

        if cached_result:
            return jsonify({"data": json.loads(cached_result)}), 200

        data_db = get_data_db()
        result = data_db.query(PeakResult).filter(PeakResult.id == id).first()
        if not result:
            return jsonify({"error": "Data not found."}), 404

        data_redis_client.setex(redis_key, 86400, json.dumps(result.to_dict()))

        return jsonify({"data": result.to_dict()}), 200

    except IntegrityError:
        if data_db:
            data_db.rollback()
        return jsonify({"error": "Something Went Wrong!"}), 500

    except Exception as e:
        print(f"Exception: {e}")
        return jsonify({"error": "Internal server error."}), 500

    finally:
        if data_db:
            data_db.close()
