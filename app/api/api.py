from flask import Blueprint, request, jsonify
from .algorithm import calculate_potholes
from .algorithm import z_thresh, z_diff
from .. import easy_db

api = Blueprint('api', __name__)


@api.route('/store_data', methods=['POST'])
def store_data():
    json_data = request.get_json(force=True)
    # Readings format timestamp: (long, lat, z_acceleration)Search Results
    # Web result with site links
    # Latitude and Longitude
    # example_input = {
    #     "2018-12-25 09:27:53": {
    #         "long": 123,
    #         "lat": 42,
    #         "z_acc": 2.3
    #     },
    #     "2018-12-26 09:27:53": {
    #         "long": 122,
    #         "lat": 43,
    #         "z_acc": -1.9
    #     }
    # }
    sensor_readings = json_data.get('sensor_readings')
    # Store z acceleration values in database (key: timestamp, val: acceleration)
    for key, val in sensor_readings.items():
        long = val["long"]
        lat = val['lat']
        z_acceleration = val["z_acc"]
        easy_db.execute(f"INSERT INTO raw_data VALUES (point({long}, {lat}), '{key}', {z_acceleration})")
    # Process window of acceleration values
    pothole_locations = calculate_potholes(z_acceleration)
    found_potholes = False if pothole_locations == [] else True

    if found_potholes:
        # Store the potholes into database
        for long, lat, severity in pothole_locations:
            easy_db.execute(f"INSERT INTO pothole VALUES (point({long}, {lat}), {severity})")
        result = {
            'success': True,
            'found_pothole': True,
            'locations': pothole_locations,
        }
    else:
        result = {
            'success': True,
            'found_pothole': False,
            'locations': None,
        }
    return jsonify(result)


@api.route('/fetch_potholes', methods=['GET'])
def fetch_potholes():
    potholes = easy_db.execute("SELECT location, severity, time FROM pothole")
    return jsonify({'success': True, 'result': [dict(row) for row in potholes]})

@api.route('/ingest_all', methods=['POST'])
def ingest_all():
    json_data = request.get_json(force=True)
    i = 0
    while 1:
        if str(i) in json_data:
            val =json_data[str(i)]
            time = val["time"]
            long = val["long"]
            lat = val['lat']
            z_acceleration = val["z_acc"]
            easy_db.execute(f"INSERT INTO raw_data VALUES ({i}, point({long}, {lat}), '{time}', {z_acceleration})")
            i += 1
        else:
            break
    result = {
        'success': True,
        'number_data': i,
    }
    return jsonify(result)

@api.route('/compute_and_get_potholes', methods=['GET'])
def update_potholes():
    all_points = easy_db.execute("SELECT location[0] as long, location[1] as lat, time, z FROM raw_data order by id;")
    params = []
    temp = []
    i = 0
    for row in all_points:
        if i == 50:
            params.append(list(temp))
            temp = []
            i = 0
        temp.append(dict(row))
        i += 1
    for i in params:
        pothole_locations = z_thresh(i)
        found_potholes = False if pothole_locations == [] else True
        for long, lat, severity in pothole_locations:
            easy_db.execute(f"INSERT INTO pothole VALUES (point({long}, {lat}), {severity})")

    #z_thresh(dict(params))
    result = {
        'success': True,
    }
    return jsonify(result)