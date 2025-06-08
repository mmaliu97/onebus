import folium
import os
from ..models.bus_models import transit_duration
from pathlib import Path


def map_maker(lat,lon,all_possible_stops, poi_df):
    '''
    Helper function to create the folium make, deletes current map made and re makes it with new data
    map will automatically be zoomed into the users location

    Arguments:
        - origin_stop: bus stop name of the origin bus stop
        - lat: current latitude of the user 
        - lon: current longitude of the user
        - all_busstops: all bus stops that user can get to given that bus number
        - poi_df: dataframe of POIs retrieved from OSMNX
        - stop_times_df: dataframe of stops_times.txt from GTFS data

    Returns:
        - map.html: folium map that is zoomed in
    '''


    # delete html file
    map_html_path = 'templates/map.html'
    
    # Clear existing map HTML file if it exists
    if os.path.exists(map_html_path):
        with open(map_html_path, 'w') as file:
            file.write('')

    map = folium.Map(location=[lat, lon], zoom_start=12)


    # Adding bus stops
    for index, row in all_possible_stops.iterrows():
        bus_stop_lat = row['stop_lat']
        bus_stop_lon = row['stop_lon']
        stop = row['stop_name']
        headsign = row['trip_headsign']
        
        popup_text = folium.Html(f"Bus Station: {stop} heading towards {headsign}", script = True)
        
        # Add a marker for each row to the map
        folium.Marker(
            location = [bus_stop_lat, bus_stop_lon], 
            popup=folium.Popup(popup_text, parse_html=True, max_width=300),
            icon=folium.Icon(color='black' ,icon='bus', prefix='fa')).add_to(map)

    # Iterate over the rows of the DataFrame
    for index, row in poi_df.iterrows():
        poi_lat = row.geometry.y
        poi_lon = row.geometry.x
        poi_busstop = str(row['stop_name'])
        poi_bus = row['route_id']
        poi_name = row['name']
        num_stops = row['stop_sequence'] - row['first_stop_number']
        poi_amenity = row['amenity']
        icon_name = row['icon']
        icon_color = row['color']
        # print(f'printing {poi_name}')
        
        popup_text = folium.Html(f"Take bus {poi_bus} for {num_stops} stops <br> Closest bus stop: {poi_busstop}.<br>Name of POI: {poi_name}.<br>Type of POI: {poi_amenity}.<br>.", script = True)

        # Add a marker for each row to the map
        folium.Marker(
            location = [poi_lat, poi_lon], 
            popup=folium.Popup(popup_text, parse_html=True, max_width=300),
            icon=folium.Icon(color=icon_color ,icon=icon_name, prefix='fa')).add_to(map)
        
    folium.Marker(
    location = [lat, lon], 
    popup='Home',
    icon=folium.Icon(color='green' ,icon='home', prefix='fa')).add_to(map)

 
    # 1. Get the project root path (assuming mapping.py is in utils/)
    current_dir = Path(__file__).parent  # Gets utils/ folder
    project_root = current_dir.parent    # Goes up one level to project_root

    # 2. Define the full template path
    template_path = project_root / "templates" / "map.html"

    # 3. Ensure directory exists
    template_path.parent.mkdir(exist_ok=True)

    # 4. Save the file
    map.save(str(template_path))  # Folium needs string path
    print("map has been saved")