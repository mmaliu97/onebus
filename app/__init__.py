# app/__init__.py
from flask import Flask
from .routes import main_bp
from .utils.data_loader import read_gcs_csv

def create_app():
    app = Flask(__name__, template_folder="templates")
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.secret_key = 'mliu'  # Should move to config.py and use env var
    
    # Initialize data
    app.config['stops_df'] = read_gcs_csv('stops.csv')
    app.config['trips_df'] = read_gcs_csv('e_trips.csv')
    app.config['stop_times_df'] = read_gcs_csv('stop_times.csv')
    app.config['filtered_poi_df'] = read_gcs_csv('filtered_pois.csv')
    
    # Register blueprints
    app.register_blueprint(main_bp)
    
    return app