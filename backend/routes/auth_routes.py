from flask import Blueprint
from controllers.auth_controller import register, login, logout, refresh_token, google_login, change_password

auth_blueprint = Blueprint('auth', __name__)

# Define the routes
auth_blueprint.route('/register', methods=['POST'])(register)
auth_blueprint.route('/login', methods=['POST'])(login)
auth_blueprint.route('/logout', methods=['POST'])(logout)
auth_blueprint.route('/refreshtoken', methods=['POST'])(refresh_token)
auth_blueprint.route('/google-login', methods=['POST'])(google_login)
auth_blueprint.route('/change-password', methods=['POST'])(change_password)
