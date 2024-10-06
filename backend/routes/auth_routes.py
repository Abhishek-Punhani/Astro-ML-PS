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
    get_user_profile,
    change_password,
    resendChangeOtp,
    verifyChangeOtp,
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
auth_blueprint.route("/profile", methods=["GET"])(get_user_profile)
auth_blueprint.route("/change-password", methods=["POST"])(change_password)
auth_blueprint.route("/verify-change-password", methods=["POST"])(verifyChangeOtp)
auth_blueprint.route("/resend-change-otp", methods=["POST"])(resendChangeOtp)
