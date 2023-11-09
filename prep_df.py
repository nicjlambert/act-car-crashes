import requests
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import folium
import webbrowser

# URL of the JSON data
url = 'https://www.data.act.gov.au/resource/6jn4-m8rx.json'

# Fetch the data from the URL
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    # Convert the JSON data into a DataFrame
    data = response.json()
    df = pd.DataFrame(data)

    # Selecting relevant columns for clustering (assuming these columns are present)
    # Here, we use 'latitude' and 'longitude'. Additional features can be included as needed.
    if 'latitude' in df.columns and 'longitude' in df.columns:
        # Convert latitude and longitude to numeric
        df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
        df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')

        # Drop rows with missing values in these columns
        df.dropna(subset=['latitude', 'longitude'], inplace=True)

        # Standardize the data
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(df[['latitude', 'longitude']])

        # Apply KMeans clustering
        kmeans = KMeans(n_clusters=3, random_state=0)
        kmeans.fit(scaled_features)

        # Add cluster labels to the DataFrame
        df['cluster'] = kmeans.labels_

        # Create a map centered around the mean latitude and longitude
        map_center = [df['latitude'].mean(), df['longitude'].mean()]
        map = folium.Map(location=map_center, zoom_start=12)

        # Colors for different clusters
        colors = ['red', 'green', 'blue']

        # Add markers to the map
        for idx, row in df.iterrows():
            folium.CircleMarker(
                location=[row['latitude'], row['longitude']],
                radius=5,
                color=colors[row['cluster']],
                fill=True,
                fill_color=colors[row['cluster']]
            ).add_to(map)

        # Save the map to an HTML file
        map.save('traffic_crash_clusters.html')
        webbrowser.open('traffic_crash_clusters.html')

        result = "Map with traffic crash clusters created successfully."
    else:
        result = "Required columns 'latitude' and 'longitude' are not present in the dataset."

else:
    result = "Failed to retrieve data. Status code: " + str(response.status_code)

result
