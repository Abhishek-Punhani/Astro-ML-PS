import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
from astropy.io import fits
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks, peak_prominences


def gaussian_smoothing(data, sigma=2):
    return gaussian_filter1d(data, sigma=sigma)


def riseTime(Data, d_new, peaks_dist, peaks_dist_unprocess):
    rise_time = []
    left = []
    for i in peaks_dist:
        j = i
        while d_new[j] - d_new[j - 1] >= -0.5:
            j -= 1
            if j == 0:
                break
        left.append(j)
    for a in range(peaks_dist.size):
        rise_time.append(abs(Data['TIME'][peaks_dist[a]] - Data['TIME'][left[a]]))

    return rise_time, left


def decayTime(Data, d_new, peaks_dist, peaks_dist_unprocess):
    decay_time = []
    right = []
    for i in peaks_dist:
        j = i
        while d_new[j] - d_new[j + 1] >= -0.5:
            j += 1
            if j == Data['RATE'].size - 1:
                break
        right.append(j)
    for a in range(peaks_dist.size):
        decay_time.append(abs(Data['TIME'][peaks_dist[a]] - Data['TIME'][right[a]]))

    return decay_time, right


def contourInfo(Data, d_new, peaks_dist, peaks_dist_unprocess):
    prominences, _, _ = peak_prominences(d_new, peaks_dist_unprocess)
    prominences_prime, _, _ = peak_prominences(d_new, peaks_dist)
    return prominences, prominences_prime


def timesofpeaks(Data, d_new, peaks_dist, peaks_dist_unprocess):
    time_of_occurance = Data['TIME'][peaks_dist_unprocess]
    time_corresponding_peak_flux = d_new[peaks_dist_unprocess]
    max_peak_flux = max(d_new[peaks_dist_unprocess])
    average_peak_flux = np.average(d_new)
    rise_time, left = riseTime(Data, d_new, peaks_dist, peaks_dist_unprocess)
    decay_time, right = decayTime(Data, d_new, peaks_dist, peaks_dist_unprocess)
    return time_of_occurance, time_corresponding_peak_flux, max_peak_flux, average_peak_flux, rise_time, left, decay_time, right


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
    if len(set(labels)) > 1 and len(set(labels)) != 1 + (1 if -1 in labels else 0):  # Ensure more than 1 valid cluster
        non_noise_mask = labels != -1
        if len(np.unique(labels[non_noise_mask])) > 1:  # Need at least 2 clusters for silhouette score
            silhouette_avg = silhouette_score(scaled_features[non_noise_mask], labels[non_noise_mask])
        else:
            silhouette_avg = None  # No valid clusters for silhouette score
    else:
        silhouette_avg = None  # DBSCAN didn't form valid clusters

    return labels, silhouette_avg



def returnable(extension):
    data = fits.open('ch2_xsm_20240906_v1_level2' + extension)

    global Data
    Data = data[1].data

    # Apply Gaussian smoothing just once for visualization purposes
    d_new = gaussian_smoothing(Data['RATE'].flatten(), sigma=2)

    # Detect peaks on the original unsmoothed data
    peaks_dist, peaks_dist_unprocess = findpeaks(Data,  d_new)

    # Process time and peak-related features
    time_of_occurance, time_corresponding_peak_flux, max_peak_flux, average_peak_flux, rise_time, left, decay_time, right = timesofpeaks(Data, d_new, peaks_dist, peaks_dist_unprocess)
    prominences, prominences_prime = contourInfo(Data, d_new, peaks_dist, peaks_dist_unprocess)

    # Ensure all feature arrays have the same length
    min_length = min(len(rise_time), len(decay_time), len(prominences), len(peaks_dist))

    # Trim the arrays to the minimum length
    rise_time = rise_time[:min_length]
    decay_time = decay_time[:min_length]
    prominences = prominences[:min_length]
    peaks_dist = peaks_dist[:min_length]
    time_of_occurance = time_of_occurance[:min_length]
    time_corresponding_peak_flux = time_corresponding_peak_flux[:min_length]

    # Prepare feature matrix for DBSCAN
    features = np.array([
        rise_time,        # Feature 1
        decay_time,       # Feature 2
        prominences       # Feature 3
    ]).T  # Transpose to shape it properly (rows as samples, columns as features)

    # Apply DBSCAN for clustering and calculate silhouette score
    cluster_labels, silhouette_avg = apply_dbscan(features)

    returndict = {
        "x": Data['TIME'].tolist(),
        "y": d_new.tolist(),
        "time_of_occurances": time_of_occurance.tolist(),
        "time_corresponding_peak_flux": time_corresponding_peak_flux.tolist(),
        "max_peak_flux": str(max_peak_flux),
        "average_peak_flux": str(average_peak_flux),
        "rise_time": rise_time,
        "left":left,
        "decay_time": decay_time,
        "right":right,
        "prominences": prominences.tolist(),
        "cluster_labels": cluster_labels.tolist(),  # Add cluster labels for interpretation
        "silhouette_avg": silhouette_avg 
    }

    return returndict


if __name__ == "__main__":
    returndict = returnable('.lc')

    # Plot the smoothed data vs time with cluster visualization
    plt.figure(figsize=(10, 6))
    plt.plot(returndict['x'], returndict['y'] , label='Smoothed RATE', color='blue')

    # Scatter plot with different colors for different clusters based on smoothed data
    unique_labels = np.unique(returndict['cluster_labels'])
    colors = plt.colormaps['rainbow'](np.linspace(0, 1, len(unique_labels)))

    for label, color in zip(unique_labels, colors):
        label_mask = np.array(returndict['cluster_labels']) == label
        if label == -1:
            # Plot outliers based on peaks in smoothed data
            plt.scatter(np.array(returndict['time_of_occurances'])[label_mask],
                        np.array(returndict['time_corresponding_peak_flux'])[label_mask],
                        color='black', label='Outliers', s=50)
        else:
            # Plot clusters based on peaks in smoothed data
            plt.scatter(np.array(returndict['time_of_occurances'])[label_mask],
                        np.array(returndict['time_corresponding_peak_flux'])[label_mask],
                        color=color, label=f'Cluster {label}', s=50)

    plt.title('X-ray Burst Analysis with DBSCAN Clusters and Outliers (Smoothed Data)')
    plt.xlabel('Time')
    plt.ylabel('Smoothed Rate')
    plt.legend()
    plt.grid(True)
    plt.show()

    # Print the silhouette score for reference
    print(f"Silhouette Score: {returndict['silhouette_avg']}")
