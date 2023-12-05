import os
import pandas as pd
import json
from mapboxgl.viz import ClusteredCircleViz
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
color_stops = create_color_stops([1,10,50,100], colors='BrBG')

# Create the visualization
viz = ClusteredCircleViz(geojson_data,
                access_token=mapbox_access_token,
                style='mapbox://styles/mapbox/light-v10',
                center=(149, -35.30),
                color_stops = color_stops,
                radius_stops = [[1,5], [10, 10], [50, 15], [100, 20]],
                cluster_maxzoom = 10,
                cluster_radius = 25,
                opacity = 0.9,
                zoom = 10
                )

viz.scale = True
# Show the map
viz.show()
