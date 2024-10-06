import uuid
from sqlalchemy import Column, Float, JSON, String
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
    max_peak_flux = Column(Float, nullable=False)
    average_peak_flux = Column(Float, nullable=False)
    rise_time = Column(JSON, nullable=False)
    decay_time = Column(JSON, nullable=False)
    x = Column(JSON, nullable=False)
    y = Column(JSON, nullable=False)
    time_of_occurances = Column(JSON, nullable=False)
    time_corresponding_peak_flux = Column(JSON, nullable=False)
    right = Column(JSON, nullable=False)  # New field
    left = Column(JSON, nullable=False)  # New field
    silhouette_score = Column(Float)
    data_hash = Column(String(64), nullable=False)
    project_name = Column(String, nullable=False)

    def to_dict(self):
        """Convert the PeakResult object to a dictionary."""
        return {
            "id": str(self.id),  # Convert UUID to string
            "max_peak_flux": self.max_peak_flux,
            "average_peak_flux": self.average_peak_flux,
            "rise_time": self.rise_time,
            "decay_time": self.decay_time,
            "x": self.x,
            "y": self.y,
            "time_of_occurances": self.time_of_occurances,
            "time_corresponding_peak_flux": self.time_corresponding_peak_flux,
            "right": self.right,
            "left": self.left,
            "silhouette_score": self.silhouette_score,
            "data_hash": self.data_hash,
            "project_name": self.project_name,
        }

    def __repr__(self):
        return f"<PeakResult id={self.id}, max_peak_flux={self.max_peak_flux}>"
