import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID

# Create a Base class
Base = declarative_base()


class OTP(Base):
    __tablename__ = "otp"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    otp = Column(String, nullable=False)  # Changed to String
    email = Column(String(120), nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)

    @property
    def id_utf8(self):
        # Convert UUID to string and then encode as UTF-8 bytes
        return str(self.id).encode("utf-8")

    def __repr__(self):
        return f"<OTP {self.otp}, Email {self.email}, Created at {self.creation_time}>"
