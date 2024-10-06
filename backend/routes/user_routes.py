from flask import Blueprint
from controllers.user_controller import analyze, save, getData

user_blueprint = Blueprint("user", __name__)


user_blueprint.route("/analyze", methods=["POST"])(analyze)
user_blueprint.route("/save", methods=["POST"])(save)
user_blueprint.route("/get-project/<id>", methods=["GET"])(getData)
