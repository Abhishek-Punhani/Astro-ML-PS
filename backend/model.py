import numpy as np
from scipy.signal import find_peaks, peak_prominences
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
from sklearn.metrics import silhouette_score


def fun(a):
    b = a.copy()
    for i in range(a.size):
        if 2 <= i <= a.size - 3:
            b[i] = (a[i - 2] + a[i - 1] + a[i] + a[i + 1] + a[i + 2]) / 5
        else:
            b[i] = a[i]
    return b


def riseTime(Data, d_new, peaks_dist):
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
        rise_time.append(abs(Data["TIME"][peaks_dist[a]] - Data["TIME"][left[a]]))
    return rise_time, left


def decayTime(Data, d_new, peaks_dist):
    decay_time = []
    right = []
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


def contourInfo(d_new, peaks_dist_unprocess):
    prominences, _, _ = peak_prominences(d_new, peaks_dist_unprocess)
    return prominences


def timesofpeaks(Data, d_new, peaks_dist, peaks_dist_unprocess):
    time_of_occurance = Data["TIME"][peaks_dist_unprocess]
    time_corresponding_peak_flux = d_new[peaks_dist_unprocess]
    max_peak_flux = max(d_new[peaks_dist_unprocess])
    average_peak_flux = np.average(d_new)
    rise_time, left = riseTime(Data, d_new, peaks_dist)
    decay_time, right = decayTime(Data, d_new, peaks_dist)
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


def findpeaks(d_new):
    peaks_dist, _ = find_peaks(d_new, height=350, distance=500)
    return peaks_dist


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


def returnable(Data):
    d_new = fun(Data["RATE"].flatten())
    # Detect peaks on the original unsmoothed data
    peaks_dist = findpeaks(d_new)

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
    ) = timesofpeaks(Data, d_new, peaks_dist, peaks_dist)

    prominences = contourInfo(d_new, peaks_dist)

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
