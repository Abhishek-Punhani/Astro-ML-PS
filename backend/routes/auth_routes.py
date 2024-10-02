from flask import Blueprint
from controllers.auth_controller import (
    register,
    login,
    logout,
    refresh_token,
    google_login,
    verifyOtp,
    sendOtp,
    forgot_password,
    resendOtp,
    githubCallback,
)

auth_blueprint = Blueprint("auth", __name__)

# Define the routes
auth_blueprint.route("/register", methods=["POST"])(register)
auth_blueprint.route("/login", methods=["POST"])(login)
auth_blueprint.route("/logout", methods=["POST"])(logout)
auth_blueprint.route("/refreshtoken", methods=["POST"])(refresh_token)
auth_blueprint.route("/google-login", methods=["POST"])(google_login)
auth_blueprint.route("/verify-otp", methods=["POST"])(verifyOtp)
auth_blueprint.route("/resend-otp", methods=["POST"])(resendOtp)
auth_blueprint.route("/send-otp", methods=["POST"])(sendOtp)
auth_blueprint.route("/forgot-password", methods=["POST"])(forgot_password)
auth_blueprint.route("/github/callback", methods=["POST"])(githubCallback)
