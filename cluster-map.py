import requests
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler, LabelEncoder
import folium
from folium.plugins import TimestampedGeoJson

# Fetching and loading data
url = 'https://www.data.act.gov.au/resource/6jn4-m8rx.json'
response = requests.get(url)

if response.status_code != 200:
    print("Failed to retrieve data. Status code:", response.status_code)
    exit()

data = response.json()
df = pd.DataFrame(data)

# Check for required columns
if not {'x', 'y', 'crash_severity', 'crash_date'}.issubset(df.columns):
    print("Required columns are not present in the dataset.")
    exit()

# Processing data
df['latitude'] = pd.to_numeric(df['y'], errors='coerce')
df['longitude'] = pd.to_numeric(df['x'], errors='coerce')
df['crash_date'] = pd.to_datetime(df['crash_date'], errors='coerce')
df['year'] = df['crash_date'].dt.year

encoder = LabelEncoder()
df['crash_severity_encoded'] = encoder.fit_transform(df['crash_severity'])

df.dropna(subset=['latitude', 'longitude', 'crash_severity_encoded'], inplace=True)

# Standardize the data
scaler = StandardScaler()
scaled_features = scaler.fit_transform(df[['latitude', 'longitude', 'crash_severity_encoded']])

# Apply KMeans clustering
kmeans = KMeans(n_clusters=3, random_state=0)
kmeans.fit(scaled_features)
df['cluster'] = kmeans.labels_

# Preparing data for TimestampedGeoJson
features = []
for year, group in df.groupby('year'):
    for _, row in group.iterrows():
        feature = {
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [row['longitude'], row['latitude']],
            },
            'properties': {
                'time': f"{year}-01-01",
                'style': {'color': ''},
                'icon': 'circle',
                'iconstyle': {
                    'fillColor': ['red', 'green', 'blue'][row['cluster']],
                    'fillOpacity': 0.8,
                    'stroke': 'true',
                    'radius': 5
                }
            }
        }
        features.append(feature)

# Creating a map
map_center = [df['latitude'].mean(), df['longitude'].mean()]
main_map = folium.Map(location=map_center, zoom_start=12)

# Adding the Timestamped GeoJSON plugin
TimestampedGeoJson({
    'type': 'FeatureCollection',
    'features': features,
}, period='P1Y', add_last_point=True).add_to(main_map)

main_map.save('map_with_yearly_slider.html')
print("Map with traffic crash clusters created successfully.")
