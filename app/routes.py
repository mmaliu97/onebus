
# app/routes.py
from flask import Blueprint, render_template, request, redirect, url_for, session
from io import StringIO
import pandas as pd
from .models.bus_models import bus_stops_finder, real_bus_origin, three_stops_finder
from .models.poi_models import POI_getter
from .utils.mapping import map_maker
from flask import jsonify
import os
from functools import cache
from flask import current_app

main_bp = Blueprint('main', __name__)




@main_bp.route("/", methods=["GET", "POST"])
def index():
    stops_df = current_app.config['stops_df']
    trips_df = current_app.config['trips_df']
    stop_times_df = current_app.config['stop_times_df']

    result=[]
    if request.method == "POST":
        user_input = ""
        user_input = request.form.get("user_input")
        try:
            user_input = int(user_input)  # Try to convert input to a float
            result, stops_times_location_df = bus_stops_finder(user_input, trips_df, stops_df,stop_times_df)
            print(result)
            # Store the result in a session variable
            session['bus_stops'] = result
            session['bus'] = user_input

            # Redirect to the next page
            return redirect(url_for('stops_no_help', result=result))

        except ValueError:
            error_message = "Input is not a valid number."

    return render_template("index.html", result = result)

def get_busstops(bus_number, trips_df, stops_df,stop_times_df):
    bus_number = int(bus_number)
    result = bus_stops_finder(bus_number, trips_df, stops_df,stop_times_df)
    return result 


@main_bp.route("/stops_no_help", methods=["GET", "POST"])
def stops_no_help():
    stops_df = current_app.config['stops_df']
    trips_df = current_app.config['trips_df']
    stop_times_df = current_app.config['stop_times_df']
    
    # Retrieve the result from the session variable
    result = session.get('bus_stops', [])
    bus = session.get('bus', [])
    three_stops_df_json = session.get('three_stops_df')
    df = pd.read_json(StringIO(three_stops_df_json)) if three_stops_df_json else pd.DataFrame()
    if request.method == "POST":
        # get the user selection for bus stop
        
        bus_stop = ""
        bus_stop = request.form.get("bus_stop")

        time = request.form.get("time")

        result, stops_times_locations_df = bus_stops_finder(bus, trips_df, stops_df,stop_times_df)
        
        session['bus_stop'] = bus_stop
        all_busstops = real_bus_origin(time,stops_times_locations_df,bus_stop)
        amenities = ['restaurant', 'cafe', 'park','cinema','music_venue',
                'social_centre','theatre','marketplace']

        
        POI_df = POI_getter(amenities,all_busstops)

        # get lat, lng of original bus stop
        lat = stops_times_locations_df[stops_times_locations_df['stop_name'] == bus_stop].iloc[0]['stop_lat']
        lon = stops_times_locations_df[stops_times_locations_df['stop_name'] == bus_stop].iloc[0]['stop_lon']\
        
        map_maker(bus_stop, lat,lon,all_busstops,POI_df,stops_times_locations_df)
        # Redirect to the next page
        return redirect(url_for('poi'))
        # except ValueError:
        #     error_message = "Input is not a valid number."
    return render_template("stops_no_help.html", result=result, table=df.to_html(classes='table table-striped table-bordered'))

@main_bp.route("/stops", methods=["GET", "POST"])
def stops():
    stops_df = current_app.config['stops_df']
    trips_df = current_app.config['trips_df']
    stop_times_df = current_app.config['stop_times_df']
    filtered_poi_df = current_app.config['filtered_poi_df']
    
    
    # Retrieve the result from the session variable
    result = session.get('bus_stops', [])
    bus = session.get('bus', [])
    
    three_stops_df_json = session.get('three_stops_df')
    three_stops_df = pd.read_json(StringIO(three_stops_df_json)) if three_stops_df_json else pd.DataFrame()

    user_selected_stop_df = three_stops_df[three_stops_df['Bus Number'] == int(session.get('bus', []))]

    
    if request.method == "POST":
        # get the user selection for bus stop
        
        bus_stop = ""
        bus_stop = request.form.get("bus_stop")

        time = request.form.get("time")

        result, stops_times_locations_df = bus_stops_finder(bus, trips_df, stops_df,stop_times_df)
        
        session['bus_stop'] = bus_stop
        all_busstops = real_bus_origin(time,stops_times_locations_df,bus_stop)

        POI_df = POI_getter(filtered_poi_df,all_busstops)

        # get lat, lng of original bus stop
        lat = stops_times_locations_df[stops_times_locations_df['stop_name'] == bus_stop].iloc[0]['stop_lat']
        lon = stops_times_locations_df[stops_times_locations_df['stop_name'] == bus_stop].iloc[0]['stop_lon']\
        
        map_maker(bus_stop, lat,lon,all_busstops,POI_df,stops_times_locations_df)
        # Redirect to the next page
        return redirect(url_for('main.poi'))
        # except ValueError:
        #     error_message = "Input is not a valid number."
    return render_template("stops.html", result=result, table=user_selected_stop_df.to_html(classes='table table-striped table-bordered'))

# @main_bp.route('/prompt_location')
# def prompt_location():
#     return render_template('prompt_location.html')

@main_bp.route('/get_data', methods=["GET",'POST'])
def get_data():
    stops_df = current_app.config['stops_df']
    trips_df = current_app.config['trips_df']
    stop_times_df = current_app.config['stop_times_df']
    try:
        # Get latitude and longitude from the request
        data = request.get_json()
        lat = float(data['latitude'])
        lon = float(data['longitude'])

        # Call your Python function with lat and lon
        three_stops_df = three_stops_finder(stop_times_df, trips_df,stops_df, lat, lon)
        print(three_stops_df)
        # Convert DataFrame to HTML table
        table_html = three_stops_df.to_html(classes='table table-striped table-bordered')
        # Store DataFrame in session
        session['three_stops_df'] = three_stops_df.to_json()
        # Render the HTML template with the DataFrame table
        return render_template('bus_info.html', table_html=table_html)
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    
@main_bp.route("/bus_info", methods=["GET",'POST'])
def bus_info():
    stops_df = current_app.config['stops_df']
    trips_df = current_app.config['trips_df']
    stop_times_df = current_app.config['stop_times_df']
    three_stops_df_json = session.get('three_stops_df')

    # df = pd.read_json(three_stops_df_json) if three_stops_df_json else pd.DataFrame()
    three_stops_df = pd.read_json(StringIO(three_stops_df_json)) if three_stops_df_json else pd.DataFrame()
    
    result=[]
    if request.method == "POST":
        user_input = ""
        user_input = request.form.get("user_input")
        try:
            user_input = int(user_input)  # Try to convert input to a float
            result, stops_times_location_df = bus_stops_finder(user_input, trips_df, stops_df,stop_times_df)

            # Store the result in a session variable
            session['bus_stops'] = result
            session['bus'] = user_input


            # Redirect to stops page - no need to pass parameters
            return redirect(url_for('main.stops'))  # Just reference the endpoint

        except ValueError:
            error_message = "Input is not a valid number."

    return render_template('bus_info.html', table=three_stops_df.to_html(classes='table table-striped table-bordered'))

@main_bp.route("/poi")
def poi():
    return render_template("poi.html")

@main_bp.route("/updates")
def updates():
    return render_template("updates.html")
