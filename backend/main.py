from flask import Flask
from flask_cors import CORS
from flask_session import Session
from routes.auth_routes import auth_blueprint
from routes.user_routes import user_blueprint
from config import Config
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# CORS Configuration
cors_options = {
    "supports_credentials": True,
    "origins": [os.getenv("CLIENT_URI")],
}
CORS(app, resources={r"/*": cors_options})

# Load configuration
app.config.from_object(Config)

# Initialize session
Session(app)

# Register Blueprints
app.register_blueprint(auth_blueprint, url_prefix="/auth")
app.register_blueprint(user_blueprint, url_prefix="/user")

# Error handling
@app.errorhandler(404)
def not_found_error(error):
    return {"error": {"status": 404, "message": "Page Not Found!"}}, 404

@app.errorhandler(500)
def internal_server_error(error):
    return {"error": {"status": 500, "message": "Internal Server Error!"}}, 500

if __name__ == "__main__":
    app.run(debug=True, port=8080)
