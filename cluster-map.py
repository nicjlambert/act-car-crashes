import os
import requests
import pandas as pd
import geojson
from mapboxgl.viz import CircleViz
from mapboxgl.utils import create_color_stops

def fetch_data(url, local_cache_file):
    if os.path.exists(local_cache_file):
        with open(local_cache_file, 'r') as file:
            data = json.load(file)
    else:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            with open(local_cache_file, 'w') as file:
                json.dump(data, file)
        else:
            raise ConnectionError(f"Failed to retrieve data. Status code: {response.status_code}")
    return data

def preprocess_data(data):
    df = pd.DataFrame(data)
    crash_counts = df.groupby('suburb_location').size().reset_index(name='crash_count')
    df = df.merge(crash_counts, on='suburb_location', how='left')
    high_risk_threshold = df['crash_count'].quantile(0.75)
    df['risk_level'] = np.where(df['crash_count'] >= high_risk_threshold, 'High', 'Normal')
    return df

def create_geojson(df):
    features = [
        geojson.Feature(
            geometry=geojson.Point((float(item["location"]["longitude"]), float(item["location"]["latitude"]))),
            properties={key: item[key] for key in item if key != 'location'}
        )
        for item in df.to_dict(orient='records')
    ]
    return geojson.FeatureCollection(features)

def create_viz(geojson_data, access_token):
    count_color_stops = create_color_stops([1, 10, 50, 100], colors='Blues')
    count_viz = CircleViz(
        geojson_data,
        access_token=access_token,
        color_property="crash_count",
        color_stops=count_color_stops,
        center=(149, -35.30),
        zoom=10
    )
    return count_viz

# Main workflow
url = 'https://www.data.act.gov.au/resource/6jn4-m8rx.json'
local_cache_file = 'data_cache.json'
mapbox_access_token = os.getenv('MAPBOX_ACCESS_TOKEN')
if mapbox_access_token is None:
    raise ValueError("Mapbox access token not found in environment variables.")

# Fetch, preprocess data, and create visualization
data = fetch_data(url, local_cache_file)
df = preprocess_data(data)
geojson_data = create_geojson(df)
viz = create_viz(geojson_data, mapbox_access_token)
viz.show()