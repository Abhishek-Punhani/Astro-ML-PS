from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
import os
import dotenv

# Load environment variables from .env file
dotenv.load_dotenv()

# Configure your database URI
DATABASE_URI = os.getenv("DATABASE_URL", 'sqlite:///mydatabase.db')  # Use SQLite or any other DB

# Create a new SQLAlchemy engine
engine = create_engine(DATABASE_URI)

# Create a Base class for SQLAlchemy
Base = declarative_base()


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

# Function to create all tables defined in the models
def create_tables(engine):
    Base.metadata.create_all(engine)

# Create the tables if they don't exist
create_tables(engine)
