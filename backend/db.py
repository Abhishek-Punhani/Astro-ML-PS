from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
import os
import dotenv
import logging

# Load environment variables from .env file
dotenv.load_dotenv()

# Configure logging
logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

# Get the database URI from environment variables
DATABASE_URI = os.getenv("DATABASE_URL")  # Correct usage here

if DATABASE_URI is None:
    raise ValueError("DATABASE_URL environment variable not set.")

print(f"Connecting to database at: {DATABASE_URI}")  # For debugging

# Create a new SQLAlchemy engine
engine = create_engine(DATABASE_URI)  # Use the variable here

# Create a Base class for SQLAlchemy
Base = declarative_base()

# Create a configured "Session" class
Session = scoped_session(sessionmaker(bind=engine))


def get_db():
    """Returns a database session."""
    return Session()


def close_db():
    """Closes the database session."""
    Session.remove()


def create_tables(engine):
    """Function to create all tables defined in the models."""
    Base.metadata.create_all(engine)


# Create the tables if they don't exist
create_tables(engine)
