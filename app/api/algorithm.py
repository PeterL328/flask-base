import pandas as pd
import numpy as np

# tuned thresholds for z_thresh
THRESH_LOWER = 1.5
THRESH_UPPER = 2.5
THRESH_SEVERITY = 4
DIFF = 1
DIFF_SEVERITY = 0.5

def calculate_potholes(z_accelerations):
    # returns a list of tuple containing long lat coordinates and severity level for potholes
    example_result = [(95, 40, 2), (54, 23, 1)]
    return example_result


def z_thresh(sensor_readings):
    lon = lat = 0
    pothole = False
    max_z = THRESH_UPPER
    min_z = THRESH_LOWER
    result = []
    for val in sensor_readings:
        z_acceleration = val["z_acc"]
        long = val["long"]
        lat = val["lat"]
        print(long, lat)
        if z_acceleration <= THRESH_LOWER or z_acceleration >= THRESH_UPPER:
            pothole = True 
            max_z = max(max_z, z_acceleration)
            min_z = min(min_z, z_acceleration)
            severity = 1 if max_z - min_z > THRESH_SEVERITY else 2
            result.append((long, lat, severity))
    return merge(result)

def z_diff(sensor_readings):
    lon = lat = 0
    pothole = False
    result = []
    prev_data = None
    for key, val in sensor_readings.items():
        if prev_data != None:
            z_acceleration = val["z_acc"]
            current_diff = abs(z_acceleration - prev_data["z_acc"])
            if current_diff >= DIFF:
                pothole = True 
                severity = 2 if current_diff * DIFF_SEVERITY > DIFF else 1
                result.append((val["long"], val['lat'], severity))
        prev_data = val
    return merge(result)

def merge(dataset):
    if len(dataset) == 1:
        return dataset
    lon = dataset[0][0]
    lat = dataset[0][1]
    severity = dataset[0][2]
    for i in range(1, len(dataset)):
        lon = (dataset[i][0] + lon)/2
        lat = (dataset[i][1] + lat)/2
        severity = max(dataset[i][2], severity)
    return [(lon, lat, severity)]

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
