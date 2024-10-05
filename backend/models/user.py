import uuid
from sqlalchemy import Column, String, Boolean
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.mutable import MutableList

# Create a Base class
Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    username = Column(String, nullable=False)
    isVerified = Column("isVerified", Boolean, default=False, nullable=False)
    
    # Use MutableList to track changes in the ARRAY field
    peak_result_ids = Column(MutableList.as_mutable(ARRAY(UUID(as_uuid=True))), default=list, nullable=False)

    @property
    def id_utf8(self):
        # Convert UUID to string and then encode as UTF-8 bytes
        return str(self.id).encode("utf-8")

    def __repr__(self):
        return (
            f"<User {self.username}, Email {self.email}, Verified: {self.isVerified}>"
        )
