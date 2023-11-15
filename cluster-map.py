import requests
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler, LabelEncoder
import folium
import webbrowser

url = 'https://www.data.act.gov.au/resource/6jn4-m8rx.json'
response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    df = pd.DataFrame(data)

    if 'x' in df.columns and 'y' in df.columns and 'crash_severity' in df.columns:
        df['latitude'] = pd.to_numeric(df['y'], errors='coerce')
        df['longitude'] = pd.to_numeric(df['x'], errors='coerce')

        # Encode 'crash_severity'
        encoder = LabelEncoder()
        df['crash_severity_encoded'] = encoder.fit_transform(df['crash_severity'])

        df.dropna(subset=['latitude', 'longitude', 'crash_severity_encoded'], inplace=True)

        # Standardize the data
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(df[['latitude', 'longitude', 'crash_severity_encoded']])

        kmeans = KMeans(n_clusters=3, random_state=0)
        kmeans.fit(scaled_features)

        df['cluster'] = kmeans.labels_

        map_center = [df['latitude'].mean(), df['longitude'].mean()]
        map = folium.Map(location=map_center, zoom_start=12)
        colors = ['red', 'green', 'blue']

        for idx, row in df.iterrows():
            folium.CircleMarker(
                location=[row['latitude'], row['longitude']],
                radius=5,
                color=colors[row['cluster']],
                fill=True,
                fill_color=colors[row['cluster']]
            ).add_to(map)

        map.save('map.html')
        result = "Map with traffic crash clusters created successfully."
        
    else:
        result = "Required columns are not present in the dataset."

else:
    result = "Failed to retrieve data. Status code: " + str(response.status_code)

print(result)