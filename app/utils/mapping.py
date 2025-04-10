import folium
import os
from ..models.bus_models import transit_duration
from pathlib import Path


def map_maker(origin_stop, lat,lon,all_busstops, poi_df, stop_times_df):
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


    # Create a Folium map centered on a specific location
    map = folium.Map(location=[lat, lon], zoom_start=16)
    # print(all_busstops.iloc[:1])
    folium.Marker(
        location = [lat, lon], 
        popup=folium.Popup(all_busstops.iloc[0]['stop_name'], parse_html=True, max_width=300),

        icon=folium.Icon(color='darkblue' ,icon='home', prefix='fa')).add_to(map)
    
    for index, row in all_busstops.iloc[1:].iterrows():
        poi_lat = row['stop_lat']
        poi_lon = row['stop_lon']
        
        # Add a marker for each row to the map
        folium.Marker(
            location = [poi_lat, poi_lon], 
            popup=folium.Popup(row['stop_name'], parse_html=True, max_width=300),
            icon=folium.Icon(color='black' ,icon='bus', prefix='fa')).add_to(map)

    # Iterate over the rows of the DataFrame
    for index, row in poi_df.iterrows():
        poi_lat = row.geometry.y
        poi_lon = row.geometry.x
        poi_busstop = str(row['stop_name'])
        poi_name = row['name']
        poi_amenity = row['amenity']
        icon_name = row['icon']
        icon_color = row['color']
        time = transit_duration(origin_stop,poi_busstop,stop_times_df)
        # print(f'printing {poi_name}')
        
        popup_text = folium.Html(f"Closest bus stop: {poi_busstop}.<br>Name of POI: {poi_name}.<br>Type of POI: {poi_amenity}.<br>Bus journey: {time} minutes.", script = True)

        # Add a marker for each row to the map
        folium.Marker(
            location = [poi_lat, poi_lon], 
            popup=folium.Popup(popup_text, parse_html=True, max_width=300),
            icon=folium.Icon(color=icon_color ,icon=icon_name, prefix='fa')).add_to(map)


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