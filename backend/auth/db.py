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

# Get the database URIs from environment variables
AUTH_DB_URI = os.getenv("AUTH_DB_URI")  # For authentication-related tables
OTP_DB_URI = os.getenv("OTP_DB_URI")  # For OTP-related tables
DATA_DB_URI = os.getenv("DATA_DB_URI")  # For general data-related tables

# Validate that all URIs are set
if not all([AUTH_DB_URI, OTP_DB_URI, DATA_DB_URI]):
    raise ValueError("One or more database environment variables are not set.")

print(
    f"Connecting to databases at: auth_db={AUTH_DB_URI}, otp_db={OTP_DB_URI}, data_db={DATA_DB_URI}"
)  # For debugging

# Create SQLAlchemy engines for each database
auth_engine = create_engine(AUTH_DB_URI)
otp_engine = create_engine(OTP_DB_URI)
data_engine = create_engine(DATA_DB_URI)

# Create separate Base classes for each database
AuthBase = declarative_base()
OtpBase = declarative_base()
DataBase = declarative_base()

# Create scoped sessions for each database
AuthSession = scoped_session(sessionmaker(bind=auth_engine))
OtpSession = scoped_session(sessionmaker(bind=otp_engine))
DataSession = scoped_session(sessionmaker(bind=data_engine))


# Create helper functions to get the correct database session
def get_auth_db():
    """Returns a session for the auth database."""
    return AuthSession()


def get_otp_db():
    """Returns a session for the otp database."""
    return OtpSession()


def get_data_db():
    """Returns a session for the data database."""
    return DataSession()


# Close session for each database
def close_auth_db():
    AuthSession.remove()


def close_otp_db():
    OtpSession.remove()


def close_data_db():
    DataSession.remove()


# Function to create all tables for all databases
def create_tables():
    """Creates all tables for each database."""
    AuthBase.metadata.create_all(auth_engine)
    OtpBase.metadata.create_all(otp_engine)
    DataBase.metadata.create_all(data_engine)


# Call create_tables to ensure tables are created
create_tables()

print("Tables created in all databases successfully.")
