from sqlalchemy import Column, Integer, String, Float, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import numpy as np
import json
import codecs
import matplotlib.pyplot as plt
from astropy.io import fits
from scipy.interpolate import make_interp_spline
from scipy.interpolate import interp1d
from scipy.signal import find_peaks, peak_prominences

# Define the base class for SQLAlchemy
Base = declarative_base()

# Define the User model
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(80), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password = Column("password", String(255), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

# Define the PeakResult model to store data processing results
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


# Function to create all tables defined in the models
def create_tables(engine):
    Base.metadata.create_all(engine)


# Initialize SQLAlchemy engine and session
engine = create_engine('sqlite:///mydatabase.db')  # Use SQLite or any other DB
Session = sessionmaker(bind=engine)
session = Session()

# Function to process FITS data and save results in the database
def process_and_save(extension, user_id):
    data = returnable(extension)  # Process the FITS data
    max_peak_flux = float(data['max_peak_flux'])
    average_peak_flux = float(data['average_peak_flux'])
    rise_time = json.dumps(data['rise_time'])  # Store list as JSON string
    decay_time = json.dumps(data['decay_time'])

    # Save the result in the database
    peak_result = PeakResult(
        user_id=user_id,
        max_peak_flux=max_peak_flux,
        average_peak_flux=average_peak_flux,
        rise_time=rise_time,
        decay_time=decay_time
    )
    session.add(peak_result)
    session.commit()

    print(f"Results for user {user_id} saved successfully!")


# Data processing functions (already defined)
def fun(a):
    b = a.copy()
    for i in range(a.size):
        if i != 0 and i != a.size-1:
            b[i] = (a[i-1] + a[i+1] + a[i]) / 3
        else:
            b[i] = a[i]
    return b

def riseTime(Data, d_new, peaks_dist, peaks_dist_unprocess):
    rise_time = []
    left = []
    leftval = []
    for i in peaks_dist:
        j = i
        while d_new[j] - d_new[j - 1] >= -0.5:
            j -= 1
            if j == 0:
                break
        left.append(j)
    for a in range(peaks_dist.size):
        rise_time.append(abs(Data['TIME'][peaks_dist[a]] - Data['TIME'][left[a]]))
        leftval.append(float(Data['TIME'][left[a]]))

    return rise_time, leftval

def decayTime(Data, d_new, peaks_dist, peaks_dist_unprocess):
    decay_time = []
    right = []
    rightval = []
    for i in peaks_dist:
        j = i
        while d_new[j] - d_new[j + 1] >= -0.5:
            j += 1
            if j == Data['RATE'].size - 1:
                break
        right.append(j)
    for a in range(peaks_dist.size):
        decay_time.append(abs(Data['TIME'][peaks_dist[a]] - Data['TIME'][right[a]]))
        rightval.append(Data['TIME'][right[a]])

    return decay_time, rightval

def contourInfo(Data, d_new, peaks_dist, peaks_dist_unprocess):
    prominences, _, _ = peak_prominences(Data['RATE'], peaks_dist_unprocess)
    contour_heights = Data['RATE'][peaks_dist_unprocess] - prominences

    prominences_prime, _, _ = peak_prominences(d_new, peaks_dist)
    contour_heights_prime = d_new[peaks_dist] - prominences_prime

    return prominences, contour_heights, prominences_prime, contour_heights_prime

def timesofpeaks(Data, d_new, peaks_dist, peaks_dist_unprocess):
    time_of_occurance = Data['TIME'][peaks_dist_unprocess]
    time_corresponding_peak_flux = Data['RATE'][peaks_dist_unprocess]
    max_peak_flux = max(Data['RATE'][peaks_dist_unprocess])
    average_peak_flux = np.average(Data['RATE'])
    rise_time, left = riseTime(Data, d_new, peaks_dist, peaks_dist_unprocess)
    decay_time, right = decayTime(Data, d_new, peaks_dist, peaks_dist_unprocess)
    return time_of_occurance, time_corresponding_peak_flux, max_peak_flux, average_peak_flux, rise_time, left, decay_time, right

def findpeaks(Data, d_new):
    all_peaks, _ = find_peaks(Data['RATE'])
    peaks_dist, _ = find_peaks(d_new, height=350, distance=500)
    peaks_dist_unprocess, _ = find_peaks(Data['RATE'], height=350, distance=500)
    return peaks_dist, peaks_dist_unprocess

def returnable(extension):
    data = fits.open('icdata' + extension)
    Data = data[1].data
    d_new = fun(Data['RATE'].flatten())
    for i in range(100):
        d_new = fun(d_new)
    peaks_dist, peaks_dist_unprocess = findpeaks(Data, d_new)
    time_of_occurance, time_corresponding_peak_flux, max_peak_flux, average_peak_flux, rise_time, left, decay_time, right = timesofpeaks(Data, d_new, peaks_dist, peaks_dist_unprocess)
    prominences, contour_heights, prominences_prime, contour_heights_prime = contourInfo(Data, d_new, peaks_dist, peaks_dist_unprocess)

    returndict = {
        "x": Data['TIME'].tolist(),
        "y": d_new.tolist(),
        "time_of_occurances": time_of_occurance.tolist(),
        "time_corresponding_peak_flux": time_corresponding_peak_flux.tolist(),
        "max_peak_flux": str(max_peak_flux),
        "average_peak_flux": str(average_peak_flux),
        "rise_time": rise_time,
        "left": left,
        "decay_time": decay_time,
        "right": right,
        "prominences": prominences.tolist(),
        "contour_heights": contour_heights.tolist(),
        "prominences_prime": prominences_prime.tolist(),
        "contour_heights_prime": contour_heights_prime.tolist()
    }
    return returndict


# For testing purposes
if __name__ == "__main__":
    # Create the tables if they don't exist
    create_tables(engine)

    # Process data for a user with ID 1 (example)
    process_and_save('.lc', user_id=1)

