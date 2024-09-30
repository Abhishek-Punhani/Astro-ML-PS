from flask import Blueprint, jsonify, request, g
from controllers.user_controller import (
    get_user_profile,
    change_password,
    verifyOtp,
    resendOtp,
)
import jwt
import os

user_blueprint = Blueprint("user", __name__)


user_blueprint.route("/profile", methods=["GET"])(get_user_profile)
user_blueprint.route("/change-password", methods=["POST"])(change_password)
user_blueprint.route("/verify-change-password", methods=["POST"])(verifyOtp)
user_blueprint.route("/resend-otp", methods=["POST"])(resendOtp)
