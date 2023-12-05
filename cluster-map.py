import os
import pandas as pd
import json
from mapboxgl.viz import CircleViz
from mapboxgl.utils import *
import requests
from IPython.display import IFrame
import mapclassify

# Further info:
#   https://github.com/mapbox/mapboxgl-jupyter

# Fetching and loading data
url = 'https://www.data.act.gov.au/resource/6jn4-m8rx.json'
response = requests.get(url)

if response.status_code != 200:
    print("Failed to retrieve data. Status code:", response.status_code)
    exit()

data = response.json()
df = pd.DataFrame(data)

# Access Mapbox Access Token from environment variable
mapbox_access_token = os.getenv('MAPBOX_ACCESS_TOKEN')

# Ensure the token is available
if mapbox_access_token is None:
    raise ValueError("Mapbox access token not found in environment variables.")

# Convert data to GeoJSON
features = []
for item in data:
    point = geojson.Point((float(item["location"]["longitude"]), float(item["location"]["latitude"])))
    properties = {key: item[key] for key in item if key != 'location'}
    features.append(geojson.Feature(geometry=point, properties=properties))

geojson_data = geojson.FeatureCollection(features)

# Assign color stops
category_color_stops = [['Injury', 'rgb(211,47,47)'],  
                        ['Property Damage Only', 'rgb(81,45,168)']]

# Create the visualization
viz = CircleViz(geojson_data,
                access_token=mapbox_access_token,
                style='mapbox://styles/mapbox/streets-v8',
                center=(149.06, -35.39),
                zoom=12,
                color_property='crash_severity',
                color_default='blue',
                color_function_type='match',
                color_stops=category_color_stops,
                radius=2  # size of the circles
                )

# Show the map
viz.show()
