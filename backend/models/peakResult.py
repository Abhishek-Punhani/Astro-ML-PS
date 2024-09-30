from sqlalchemy import Column, Integer, Float, JSON
from sqlalchemy.ext.declarative import declarative_base

# Create a Base class
Base = declarative_base()


class PeakResult(Base):
    __tablename__ = "peak_results"

    id = Column(Integer, primary_key=True, index=True)
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

    def __repr__(self):
        return f"<PeakResult for User {self.user_id}>"
