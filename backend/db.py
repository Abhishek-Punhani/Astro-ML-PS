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

# Define the User model
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(80), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password = Column("password", String(255), nullable=False)
    isVerified = Column(Boolean, default=False, nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

# Define the PeakResult model
class PeakResult(Base):
    __tablename__ = 'peak_results'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)  # Foreign key relation to User table
    max_peak_flux = Column(Float)
    average_peak_flux = Column(Float)
    rise_time = Column(String)  # Store as JSON-encoded string
    decay_time = Column(String)  # Store as JSON-encoded string

    def __repr__(self):
        return f'<PeakResult for User {self.user_id}>'

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
