from flask import Blueprint
from controllers.user_controller import (
    change_password,
    verifyOtp,
    resendOtp,
    analyze,
    save,
    getData,
)

user_blueprint = Blueprint("user", __name__)

user_blueprint.route("/change-password", methods=["POST"])(change_password)
user_blueprint.route("/verify-change-password", methods=["POST"])(verifyOtp)
user_blueprint.route("/resend-otp", methods=["POST"])(resendOtp)
user_blueprint.route("/analyze", methods=["POST"])(analyze)
user_blueprint.route("/save", methods=["POST"])(save)
user_blueprint.route("/get-project/<id>", methods=["GET"])(getData)
