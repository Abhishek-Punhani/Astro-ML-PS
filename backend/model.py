from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from scipy.ndimage import gaussian_filter1d
import numpy as np
import json
from astropy.io import fits
from scipy.signal import find_peaks, peak_prominences
from db import get_db
from models.peakResult import PeakResult

# Initialize your database engine
engine = create_engine('sqlite:///mydatabase.db')  # Use the same engine as db.py

# Function to process FITS data and save results in the database
def process_and_save(extension, user_id):
    data = returnable(extension)  # Process the FITS data
    max_peak_flux = float(data['max_peak_flux'])
    average_peak_flux = float(data['average_peak_flux'])
    rise_time = json.dumps(data['rise_time'])  # Store list as JSON string
    decay_time = json.dumps(data['decay_time'])
    x = json.dumps(data['x'])  
    y = json.dumps(data['y']) 
    time_of_occurances = json.dumps(data['time_of_occurances'])  
    time_corresponding_peak_flux = json.dumps(data['time_corresponding_peak_flux'])  



    # Use a session from get_db
    with get_db() as session:
        # Save the result in the database
        peak_result = PeakResult(
            user_id=user_id,
            max_peak_flux=max_peak_flux,
            average_peak_flux=average_peak_flux,
            rise_time=rise_time,
            decay_time=decay_time,
            x=x,
            y=y,
            time_of_occurances=time_of_occurances,
            time_corresponding_peak_flux=time_corresponding_peak_flux
        )
        session.add(peak_result)
        session.commit()

        print(f"Results for user {user_id} saved successfully!")

# Data processing functions
def gaussian_smoothing(data, sigma=2):
    return gaussian_filter1d(data, sigma=sigma)

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
    data = fits.open('light_cu_data' + extension)
    Data = data[1].data
    d_new = gaussian_smoothing(Data['RATE'].flatten(), sigma=2)
    for i in range(100):
        d_new = gaussian_smoothing(d_new, sigma=2)
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

