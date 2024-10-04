import uuid
from sqlalchemy import Column, Integer, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID

# Create a Base class
Base = declarative_base()


class PeakResult(Base):
    __tablename__ = "peak_results"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    user_id = Column(Integer, nullable=False)
    max_peak_flux = Column(Float, nullable=False)
    average_peak_flux = Column(Float, nullable=False)
    rise_time = Column(JSON, nullable=False)
    decay_time = Column(JSON, nullable=False)
    x = Column(JSON, nullable=False)
    y = Column(JSON, nullable=False)
    time_of_occurances = Column(JSON, nullable=False)
    time_corresponding_peak_flux = Column(JSON, nullable=False)
    silhouette_score = Column(Float)

    @property
    def id_utf8(self):
        # Convert UUID to string and then encode as UTF-8 bytes
        return str(self.id).encode("utf-8")

    def __repr__(self):
        return f"<PeakResult for User {self.user_id}>"
