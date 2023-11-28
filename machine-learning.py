from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.preprocessing import StandardScaler, LabelEncoder
import requests
import pandas as pd

# Fetching and loading data
url = 'https://www.data.act.gov.au/resource/6jn4-m8rx.json'
response = requests.get(url)

if response.status_code != 200:
    print("Failed to retrieve data. Status code:", response.status_code)
    exit()

data = response.json()
df = pd.DataFrame(data)

# Check for required columns
required_columns = {'crash_severity', 'weather_condition', 'road_condition', 'lighting_condition', 'x', 'y'}
if not required_columns.issubset(df.columns):
    print("Required columns are not present in the dataset.")
    exit()

# Feature Engineering
encoder = LabelEncoder()
df['weather_condition_encoded'] = encoder.fit_transform(df['weather_condition'])
df['road_condition_encoded'] = encoder.fit_transform(df['road_condition'])
df['lighting_condition_encoded'] = encoder.fit_transform(df['lighting_condition'])

df['crash_severity_encoded'] = encoder.fit_transform(df['crash_severity'])
features = df[['weather_condition_encoded', 'road_condition_encoded', 'lighting_condition_encoded', 'x', 'y']]
target = df['crash_severity_encoded']

# Splitting data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.2, random_state=0)

# Standardize the features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Adjusting class weights
# Giving more weight to class 1 (injury cases)
class_weights = {0: 1, 1: 10}  # Adjust this based on your specific needs

# Model Training with RandomForest
model = RandomForestClassifier(random_state=0, class_weight={0: 1, 1: 10})
model.fit(X_train_scaled, y_train)  

# Predictions
predictions = model.predict(X_test_scaled)

# Evaluation
print("Classification Report:\n", classification_report(y_test, predictions))

# Assuming model is your trained RandomForestClassifier
# and X_test_scaled is your test dataset

predicted_injuries = model.predict(X_test_scaled)

# Add predictions to your test dataset for analysis
df_test = pd.DataFrame(X_test_scaled, columns=['weather_condition', 'road_condition', 'lighting_condition', 'x', 'y'])
df_test['predicted_injury'] = predicted_injuries
