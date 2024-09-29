from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timedelta, timezone

# Create a Base class
Base = declarative_base()

class OTP(Base):
    __tablename__ = 'otp'

    id = Column(Integer, primary_key=True)
    otp = Column(String, nullable=False)  # Changed to String
    email = Column(String(120), nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)

    def __repr__(self):
        return f'<OTP {self.otp}, Email {self.email}, Created at {self.creation_time}>'
