import os
import json
import numpy as np
import pandas as pd
import json
from mapboxgl.viz import ClusteredCircleViz
from mapboxgl.utils import *
import requests

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

# Group by 'suburb_location' and create a new DataFrame with crash counts
crash_counts = df.groupby('suburb_location').size().reset_index(name='crash_count')

# Merge this back into the original DataFrame
df = df.merge(crash_counts, on='suburb_location', how='left')

# Now you have the 'crash_count' column in df and can create the 'risk_level' column
high_risk_threshold = df['crash_count'].quantile(0.75) # Or any other statistical measure
df['risk_level'] = np.where(df['crash_count'] >= high_risk_threshold, 'High', 'Normal')

# Convert the DataFrame to a JSON string
json_data = df.to_json(orient='records')

# Parse the JSON string back into a list of dictionaries, which resembles the parsed JSON data
data = json.loads(json_data)

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