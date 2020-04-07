import pandas as pd
import numpy as np


def calculate_potholes(sensor_readings):
    # returns a list of tuple containing long lat coordinates and severity level for potholes
    example_result = [(95, 40, 2), (54, 23, 1)]
    return example_result


def stdev(sensor_readings):
    # return format [(long, lat, severity), (), (), ...]
    rolling_window = 3
    threshold = 1.5
    severity_increment_in_threshold = 0.2
    readings = pd.DataFrame.from_dict(sensor_readings, orient='index').sort_index()
    std = readings["z_acc"].rolling(rolling_window).std().dropna().to_frame()
    std["have_potholes"] = std > threshold
    std = std[std["have_potholes"]]
    std['severity'] = ((std['z_acc'] - threshold) / severity_increment_in_threshold).apply(np.ceil)

    # above_threshold = above_threshold[above_threshold]
    joined = pd.merge(std, readings, left_index=True, right_index=True)
    subset = joined[['long', 'lat', 'severity']]
    tuples = [tuple(x) for x in subset.to_numpy()]
    return tuples
