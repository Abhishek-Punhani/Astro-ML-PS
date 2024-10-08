import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET")
    SESSION_TYPE = "filesystem"
    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # Set the maximum content length to 16 MB
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB