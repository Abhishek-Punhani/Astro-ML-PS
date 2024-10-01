from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import numpy as np
import json
from astropy.io import fits
from scipy.signal import find_peaks, peak_prominences
from db import get_db
from models.peakResult import PeakResult
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
from sklearn.metrics import silhouette_score

# Initialize your database engine
engine = create_engine("sqlite:///mydatabase.db")  # Ensure correct database URL


# Function to process FITS data and save results in the database
def process_and_save(extension, user_id):
    data = returnable(extension)  # Process the FITS data
    max_peak_flux = float(data["max_peak_flux"])
    average_peak_flux = float(data["average_peak_flux"])
    rise_time = json.dumps(data["rise_time"])  # Store lists as JSON strings
    decay_time = json.dumps(data["decay_time"])
    x = json.dumps(data["x"])
    y = json.dumps(data["y"])
    time_of_occurances = json.dumps(data["time_of_occurances"])
    time_corresponding_peak_flux = json.dumps(data["time_corresponding_peak_flux"])
    cluster_labels = json.dumps(data["cluster_labels"])
    silhouette_score = data.get("silhouette_avg")
    silhouette_score = silhouette_score if silhouette_score is not None else None

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
            time_corresponding_peak_flux=time_corresponding_peak_flux,
            cluster_labels=cluster_labels,
            silhouette_score=silhouette_score,
        )
        session.add(peak_result)
        session.commit()

        print(f"Results for user {user_id} saved successfully!")


def fun(a):
    b = a.copy()
    for i in range(a.size):
        if i >= 2 and i <= a.size - 3:
            b[i] = (a[i-2] + a[i-1] + a[i] + a[i+1] + a[i+2]) / 5
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
        rise_time.append(abs(Data["TIME"][peaks_dist[a]] - Data["TIME"][left[a]]))
    return rise_time, left


def decayTime(Data, d_new, peaks_dist, peaks_dist_unprocess):
    decay_time = []
    right = []
    rightval = []
    for i in peaks_dist:
        j = i
        while d_new[j] - d_new[j + 1] >= -0.5:
            j += 1
            if j == Data["RATE"].size - 1:
                break
        right.append(j)
    for a in range(peaks_dist.size):
        decay_time.append(abs(Data["TIME"][peaks_dist[a]] - Data["TIME"][right[a]]))
    return decay_time, right


def contourInfo(Data, d_new, peaks_dist, peaks_dist_unprocess):
    prominences, _, _ = peak_prominences(d_new, peaks_dist_unprocess)
    prominences_prime, _, _ = peak_prominences(d_new, peaks_dist)
    return prominences, prominences_prime


def timesofpeaks(Data, d_new, peaks_dist, peaks_dist_unprocess):
    time_of_occurance = Data["TIME"][peaks_dist_unprocess]
    time_corresponding_peak_flux = d_new[peaks_dist_unprocess]
    max_peak_flux = max(d_new[peaks_dist_unprocess])
    average_peak_flux = np.average(d_new)
    rise_time, left = riseTime(Data, d_new, peaks_dist, peaks_dist_unprocess)
    decay_time, right = decayTime(Data, d_new, peaks_dist, peaks_dist_unprocess)
    return (
        time_of_occurance,
        time_corresponding_peak_flux,
        max_peak_flux,
        average_peak_flux,
        rise_time,
        left,
        decay_time,
        right,
    )


def findpeaks(Data, d_new):
    all_peaks, _ = find_peaks(d_new)
    peaks_dist, _ = find_peaks(d_new, height=350, distance=500)
    peaks_dist_unprocess, _ = find_peaks(d_new, height=350, distance=500)
    return peaks_dist, peaks_dist_unprocess


def apply_dbscan(features):
    # Normalize the features
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features)

    # Apply DBSCAN
    dbscan = DBSCAN(eps=0.5, min_samples=5)
    labels = dbscan.fit_predict(scaled_features)

    # Calculate silhouette score for non-noise points (ignoring label -1)
    non_noise_mask = labels != -1
    if len(np.unique(labels[non_noise_mask])) > 1:
        silhouette_avg = silhouette_score(
            scaled_features[non_noise_mask], labels[non_noise_mask]
        )
    else:
        silhouette_avg = None  # No valid clusters for silhouette score

    return labels, silhouette_avg


def returnable(extension):
    data = fits.open("/home/nirved/Projects/Webdev/Inter IIT Astro SDE/MoonAnalyser/Astro-ML-PS/Chart/ch2_xsm_20240906_v1_level2" + extension)
    Data = data[1].data

    d_new = fun(Data['RATE'].flatten())

    # Detect peaks on the original unsmoothed data
    peaks_dist, peaks_dist_unprocess = findpeaks(Data, d_new)

    # Process time and peak-related features
    (
        time_of_occurance,
        time_corresponding_peak_flux,
        max_peak_flux,
        average_peak_flux,
        rise_time,
        left,
        decay_time,
        right,
    ) = timesofpeaks(Data, d_new, peaks_dist, peaks_dist_unprocess)
    prominences, prominences_prime = contourInfo(
        Data, d_new, peaks_dist, peaks_dist_unprocess
    )

    # No more trimming based on minimum length
    # Prepare feature matrix for DBSCAN
    features = np.array([rise_time, decay_time, prominences]).T

    # Apply DBSCAN for clustering and calculate silhouette score
    cluster_labels, silhouette_avg = apply_dbscan(features)

    returndict = {
        "x": Data["TIME"].tolist(),
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
        "cluster_labels": cluster_labels.tolist(),
        "silhouette_avg": silhouette_avg,
    }

    return returndict


# Commenting out plotting for now, but can be used for testing purposes
if __name__ == "__main__":
    returndict = returnable('.lc')
#     plt.figure(figsize=(10, 6))
#     plt.plot(returndict['x'], returndict['y'], label='Smoothed RATE', color='blue')
#     unique_labels = np.unique(returndict['cluster_labels'])
#     colors = plt.colormaps['rainbow'](np.linspace(0, 1, len(unique_labels)))
#     for label, color in zip(unique_labels, colors):
#         label_mask = np.array(returndict['cluster_labels']) == label
#         if label == -1:
#             plt.scatter(np.array(returndict['time_of_occurances'])[label_mask], np.array(returndict['time_corresponding_peak_flux'])[label_mask], color='black', label='Outliers', s=50)
#         else:
#             plt.scatter(np.array(returndict['time_of_occurances'])[label_mask], np.array(returndict['time_corresponding_peak_flux'])[label_mask], color=color, label=f'Cluster {label}', s=50)
#     plt.title('X-ray Burst Analysis with DBSCAN Clusters and Outliers (Smoothed Data)')
#     plt.xlabel('Time')
#     plt.ylabel('Smoothed Rate')
#     plt.legend()
#     plt.grid(True)
#     plt.show()
#     print(f"Silhouette Score: {returndict['silhouette_avg']}")
