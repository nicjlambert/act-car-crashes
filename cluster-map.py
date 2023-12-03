import os
import pandas as pd
import json
from mapboxgl.viz import CircleViz
from mapboxgl.utils import *
import requests
from IPython.display import IFrame

# Fetching and loading data
url = 'https://www.data.act.gov.au/resource/6jn4-m8rx.json'
response = requests.get(url)

if response.status_code != 200:
    print("Failed to retrieve data. Status code:", response.status_code)
    exit()

data = response.json()
df = pd.DataFrame(data)

# Convert the DataFrame to a GeoJSON format
#def df_to_geojson(df, properties, lat='y', lon='x'):
#    geojson = {'type':'FeatureCollection', 'features':[]}
#    for _, row in df.iterrows():
#        if pd.notnull(row[lat]) and pd.notnull(row[lon]):
#            feature = {'type':'Feature',
#                       'properties':{},
#                       'geometry':{'type':'Point',
#                                   'coordinates':[]}}
#            # Convert coordinates to float
#            feature['geometry']['coordinates'] = [float(row[lon]), float(row[lat])]
#            for prop in properties:
#                feature['properties'][prop] = row[prop]
#            geojson['features'].append(feature)
#    return geojson
## Columns you want to include in the properties
#properties = ['crash_id', 'crash_date', 'crash_time', 'suburb_location', 'crash_severity']
#
## Generate GeoJSON
#geojson_data = df_to_geojson(df, properties)

# Check if GeoJSON is created properly
#print(json.dumps(geojson_data, indent=2)[:500])  # Print first 500 characters for checking

# Access Mapbox Access Token from environment variable
mapbox_access_token = os.getenv('MAPBOX_ACCESS_TOKEN')

# Ensure the token is available
if mapbox_access_token is None:
    raise ValueError("Mapbox access token not found in environment variables.")

# Create a geojson Feature Collection export from a Pandas dataframe
points = df_to_geojson(df, 
                       properties=['crash_id', 'crash_date', 'crash_time', 'suburb_location', 'crash_severity'],
                       lat='x', lon='y', precision=3)

#Create a clustered circle map
color_stops = create_color_stops([1,10,50,100], colors='BrBG')

viz = ClusteredCircleViz(points,
                         access_token=mapbox_access_token,
                         color_stops=color_stops,
                         radius_stops=[[1,5], [10, 10], [50, 15], [100, 20]],
                         radius_default=2,
                         cluster_maxzoom=10,
                         cluster_radius=30,
                         label_size=12,
                         opacity=0.9,
                         center=(-95, 40),
                         zoom=3)

# Show the map
viz.show()
#viz.create_html('temp_map.html')  # Save the map to an HTML file
#IFrame('temp_map.html', width=700, height=500)  # Adjust size as needed

