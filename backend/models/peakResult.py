from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base

# Create a Base class
Base = declarative_base()


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