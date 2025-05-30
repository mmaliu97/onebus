# get bus route for each bus service

import pandas as pd
import osmnx as ox
from datetime import datetime
from datetime import timedelta
import pandas as pd
from shapely.geometry import Point, Polygon
import folium
import numpy as np
from math import radians, sin, cos, sqrt, atan2
import os

def bus_stops_finder(bus_number, trips_df, stops_df,stop_times_df ):
    '''
    This function finds all available bus stops based on a bus number

    Inputs: 
    - bus_number (integer): Bus number 
    - trips_df: dataframe of trips.txt from GTFS data
    - stops_df: dataframe of stops.txt from GTFS data
    - stop_times_df: dataframe of stops_times.txt from GTFS data

    Outputs:
    - unique_stops: Array of unique bus stops in that bus line

    '''

    route_trips = trips_df[trips_df['route_id'].isin([bus_number])]

    # By getting the unique trip headsigns we can get a trip_id that is associate to the unique trips the bus makes. A bus makes multiple duplicate trips throughout the day, but the trip_headsign remains the same
    unique_rows = route_trips.drop_duplicates(subset='trip_headsign')

    bus_trip_id= unique_rows[['trip_id','direction_id']]

    # Using the bus IDs, we can filter out the stop times for each bus unqiue bus route with the stop_times_df
    selected_stop_times = stop_times_df[stop_times_df['trip_id'].isin(bus_trip_id['trip_id'])]
    selected_stop_times = selected_stop_times.merge(bus_trip_id, on="trip_id")

    # merge into one dataframe so we can get the bus locations and bus timings
    selected_stops_times_location = selected_stop_times.merge(stops_df[['stop_name', 'stop_lat', 'stop_lon','stop_id']], on='stop_id', how='inner')
    
    # get unique stops to display for user
    unique_stops = selected_stops_times_location['stop_name'].unique()

    unique_stops = unique_stops.tolist()

    return unique_stops, selected_stops_times_location


def three_stops_finder(all_unique_stops, user_latitude, user_longitude):
    '''
    Find the closest 3 bus stops and their corresponding bus numbers (note a bus stop can have more than 1 bus going through it!)

    Arguments: 
    all_unique_stops: all unique routes from the GTFS data
    user_latitude: get this by prompting for user's location from the front end
    user_longitude: get this by prompting for user's location from the front end

    Returns:
    origin_stops: Dataframe of the 3 closest bus stops and all corresponding bus stops 
    '''

    # Calculate distances using Haversine formula
    def haversine(lat1, lon1, lat2, lon2):
        R = 6371  # Radius of the E arth in kilometers
        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)
        a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        distance = R * c
        return distance

    # Calculate distances for each bus stop
    all_unique_stops['distance'] = all_unique_stops.apply(lambda row: haversine(user_latitude, user_longitude, row['stop_lat'], row['stop_lon']), axis=1)

    # Sort bus stops by distance and get the closest stops
    closest_stops = all_unique_stops.nsmallest(3, 'distance')[[ 'stop_name', 'stop_lat', 'stop_lon', 'distance']]

    # Sort by distance (ascending) to prioritize closer stops
    sorted_stops = all_unique_stops.sort_values('distance')

    # Drop duplicates, keeping the first (closest) occurrence of each stop_name
    unique_sorted_stops = sorted_stops.drop_duplicates(subset=['stop_name'], keep='first')

    # Take the top 3 closest unique stops
    closest_stops = unique_sorted_stops.head(3)[['stop_name', 'stop_lat', 'stop_lon', 'distance']]

    # select the 3 closest bus stops
    origin_stops = all_unique_stops[all_unique_stops['stop_name'].isin(closest_stops['stop_name'])]

    origin_stops = origin_stops.sort_values(by='route_id')
    origin_stops['distance'] = (np.ceil(origin_stops['distance']*100 ) * 10).astype(int)
    origin_stops = origin_stops.rename(columns={'distance': 'distance (m)'})

    # tag the closest stops to be origin stops
    origin_stops['origin stop'] = True 
    
    return origin_stops

def all_stop_finder(origin_stops, all_unique_stops):
    '''
    Find the closest 3 bus stops and their corresponding bus numbers (note a bus stop can have more than 1 bus going through it!)

    Arguments: 
    all_unique_stops: all unique routes from the GTFS data
    origin_stops: The 3 origin bus stops near the user

    Returns:
    all_possible_stops: Dataframe of all possible stops that the user can go to based off the 3 bus stops
    '''
    # initialize subsequent stops dataframe
    subsequent_stops = pd.DataFrame()

    for index,row in origin_stops.iterrows():
        # take the stop name and the stop sequence in order to find out which are the subsequent stops
        current_sequence = row['stop_sequence']
        headsign = row['trip_headsign']
        subsequent_stops_add = all_unique_stops[(all_unique_stops['stop_sequence'] > current_sequence) & (all_unique_stops['trip_headsign'] == headsign)]
        
        subsequent_stops = pd.concat([subsequent_stops,subsequent_stops_add])
        
    subsequent_stops['origin stop'] = False
    
    all_possible_stops = pd.concat([origin_stops,subsequent_stops])
    
    return all_possible_stops

def real_bus_origin(selected_stops_times_location, bus_origins):
    '''
    Because the bus origin might change depending on the time the user departs, it is important to choose the user's bus
    stop correctly

    inputs:
    selected_stops_times_location: this dataframe contains all the stop times and locations of the bus that the user selected
    bus_origins: all possible bus stop origins 
    
    output: time appropriate bus stop
    '''
    
    time = '08:00' # default time to be 8am
    str_time = time + ':00'
    
    possible_locations = []
    
    for bus_origin in bus_origins:

        origin_sequence = selected_stops_times_location[selected_stops_times_location['stop_name'] == bus_origin ]
        last_sequence = max(selected_stops_times_location['stop_sequence'])
        min_time = timedelta(seconds=86400)

        for index_origin, row_origin in origin_sequence.iterrows():
            min_sequence = row_origin['stop_sequence']
            if min_sequence <= last_sequence:

                # reset the first sequence  
                last_sequence = min_sequence

                # calculate the time difference
                start_time = datetime.strptime(row_origin['arrival_time'], '%H:%M:%S')
                user_time = datetime.strptime(str_time, '%H:%M:%S')
                time_diff = user_time - start_time
                # if the time difference between start of bus line and user time is positive, choose that bus line 
                if time_diff > timedelta(seconds=0):
                    time_diff = min_time
                    real_origin = row_origin
                else:
                    real_origin = row_origin

        # get the trip ID and and which order is it in the list of bus stops
        selected_trip_id= real_origin['trip_id']
        selected_stop_seq = real_origin['stop_sequence']

        # find all possible bus stops the user can go to and (selected_stops_times_location['trip_id'] == selected_trip_id)
        possible_locations = possible_locations.append(selected_stops_times_location[(selected_stops_times_location['stop_sequence'] >= selected_stop_seq) & (selected_stops_times_location['trip_id'] == selected_trip_id)])

    return possible_locations



def transit_duration(origin, destination, stop_times_df):
    '''
    Helper function to caluclate the duration of the bus journey

    Arguments:
        - origin: bus stop name of the origin bus stop
        - destination: bus stop name of the destination bus stop
        - stop_times_df: dataframe of stops_times.txt from GTFS data

    Returns:
        - time_diff_mins: rounded up number of time difference
    '''

    # get the bus timings
    get_on = stop_times_df[stop_times_df['stop_name'] == origin]['departure_time'].values[0]
    get_off = stop_times_df[stop_times_df['stop_name'] == destination]['departure_time'].values[0]

    # calculate the time difference
    start_time = datetime.strptime(get_on, '%H:%M:%S')
    user_time = datetime.strptime(get_off, '%H:%M:%S')
    time_diff = user_time - start_time
    time_diff_mins = round(time_diff.total_seconds() / 60)

    return time_diff_mins

