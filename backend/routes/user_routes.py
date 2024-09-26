from flask import Blueprint
from controllers.user_controller import get_user_profile

user_blueprint = Blueprint('user', __name__)

# Define the routes
user_blueprint.route('/profile', methods=['GET'])(get_user_profile)
