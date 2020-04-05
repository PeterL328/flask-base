from flask import Blueprint, request, jsonify
from .algorithm import calculate_potholes
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