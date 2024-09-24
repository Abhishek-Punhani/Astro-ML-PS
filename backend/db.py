from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
import os
import dotenv
from model import create_tables  # Import create_tables from model.py

# Load environment variables from .env file
dotenv.load_dotenv()

# Configure your database URI
DATABASE_URI = os.getenv("DATABASE_URL")

# Create a new SQLAlchemy engine
engine = create_engine(DATABASE_URI)

# Test the connection
try:
    with engine.connect() as connection:
        print("Database connection successful!")
except Exception as e:
    print(f"Error connecting to the database: {e}")

# Create a configured "Session" class
Session = scoped_session(sessionmaker(bind=engine))

def get_db():
    """
    Returns a database session. This function should be called to interact with the database.
    """
    return Session()

def close_db():
    """
    Closes the database session.
    """
    Session.remove()

# Ensure tables are created in the database
create_tables(engine)
