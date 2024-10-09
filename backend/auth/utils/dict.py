def peak_result_to_dict(peak_result):
    return {
        "id": str(peak_result.id),
        "max_peak_flux": peak_result.max_peak_flux,
        "average_peak_flux": peak_result.average_peak_flux,
        "rise_time": peak_result.rise_time,
        "decay_time": peak_result.decay_time,
        "x": peak_result.x,
        "y": peak_result.y,
        "time_of_occurances": peak_result.time_of_occurances,
        "time_corresponding_peak_flux": peak_result.time_corresponding_peak_flux,
        "right": peak_result.right,
        "left": peak_result.left,
        "silhouette_score": peak_result.silhouette_score,
        "data_hash": peak_result.data_hash,
        "project_name": peak_result.project_name,
    }


def user_to_dict(user):
    return {
        "id": str(user.id),
        "email": user.email,
        "password": user.password,
        "username": user.username,
        "isVerified": user.isVerified,
        "peak_result_ids": [str(id) for id in user.peak_result_ids],
    }
