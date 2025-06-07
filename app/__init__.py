# app/__init__.py
from flask import Flask
from .routes import main_bp
from .utils.data_loader import read_gcs_csv

def create_app():
    app = Flask(__name__, template_folder="templates", static_folder='static')
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.secret_key = 'mliu'  # Should move to config.py and use env var
    
    # First load the raw data
    stops_df = read_gcs_csv('stops.csv')
    trips_df = read_gcs_csv('e_trips.csv')
    stop_times_df = read_gcs_csv('stop_times.csv')
    filtered_poi_df = read_gcs_csv('filtered_pois.csv')
    all_unique_stops_df = read_gcs_csv('all_unique_stops.csv')
    
    # Declaring data types
    all_unique_stops_df = all_unique_stops_df.astype({
    "trip_id":                  "object",
    "arrival_time":             "object",
    "departure_time":           "object",
    "stop_sequence":            "int64",
    "trip_headsign":            "object",
    "direction_id":             "int64",
    "route_id":                 "int64",
    "wheelchair_accessible":    "int64",
    "bikes_allowed":            "int64",
    "stop_lat":                 "float64",
    "stop_lon":                 "float64",
    "stop_name":                "object",
    "is_express":               "bool"
})
    
    trips_df = trips_df.astype({
    'route_id': 'int64',
    'service_id': 'string',
    'trip_id': 'string',
    'trip_headsign': 'string',
    'direction_id': 'int8',
    'block_id': 'string',
    'shape_id': 'string',
    'scheduled_trip_id': 'string',
    'trip_short_name': 'string',
    'wheelchair_accessible': 'int8',
    'bikes_allowed': 'int8'
})[['trip_id', 'route_id','service_id','trip_headsign','direction_id','scheduled_trip_id','trip_short_name','block_id']]  # Only keep essential columns
    
    stop_times_df = stop_times_df.astype({
    'trip_id': 'string',
    'arrival_time': 'string',
    'departure_time': 'string',
    'stop_id': 'string',
    'stop_sequence': 'int16',
    'pickup_type': 'int8',
    'drop_off_type': 'int8',
    'shape_dist_traveled': 'float32',
    'timepoint': 'int8'
})[['trip_id', 'arrival_time', 'departure_time', 'stop_sequence', 'stop_id']]  # Only necessary columns
    
    filtered_poi_df = filtered_poi_df.astype({
    'amenity': 'string',
    'name': 'string',
    'geometry': 'string',  # Will parse to POINT later
    'icon': 'string',
    'color': 'string'
})[['amenity', 'name', 'geometry', 'icon', 'color']]  # Only necessary columns
    
    # Store optimized DataFrames in app config
    app.config['stops_df'] = stops_df
    app.config['trips_df'] = trips_df
    app.config['stop_times_df'] = stop_times_df
    app.config['filtered_poi_df'] = filtered_poi_df
    app.config['all_unique_stops_df'] = all_unique_stops_df
    
    # Register blueprints
    app.register_blueprint(main_bp)
    
    return app