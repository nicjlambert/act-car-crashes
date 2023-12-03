import requests
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.utils import to_categorical

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

# Number of unique labels in target
num_classes = len(target.unique())
print(num_classes)

# Building the Shallow Neural Network
model = Sequential()
model.add(Dense(10, input_shape=(X_train_scaled.shape[1],), activation='relu'))  # One hidden layer
model.add(Dense(num_classes, activation='softmax'))  # Output layer

# Compiling the Model
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

# Preparing target data for Keras (one-hot encoding)
y_train_encoded = to_categorical(y_train, num_classes=num_classes)
y_test_encoded = to_categorical(y_test, num_classes=num_classes)

# Training the Model
model.fit(X_train_scaled, y_train_encoded, epochs=10, batch_size=32)

# Evaluating the Model
loss, accuracy = model.evaluate(X_test_scaled, y_test_encoded)
print(f'Test accuracy: {accuracy}')

# Predictions
predictions = model.predict(X_test_scaled)
predicted_classes = predictions.argmax(axis=1)

# Add predictions to your test dataset for analysis
df_test = pd.DataFrame(X_test_scaled, columns=['weather_condition', 'road_condition', 'lighting_condition', 'x', 'y'])
df_test['predicted_crash_severity'] = predicted_classes

# Example new data (needs to be in the same format as the training data)
new_data = {
    'weather_condition': ['Sunny', 'Rainy'],
    'road_condition': ['Dry', 'Wet'],
    'lighting_condition': ['Daylight', 'Dark'],
    'x': [149.094072, 200],
    'y': [-35.2013155, 250]
}
new_df = pd.DataFrame(new_data)

def safe_transform(encoder, column, default_value):
    # Create a new column with transformed values or a default value for unknown categories
    return [encoder.transform([value])[0] if value in encoder.classes_ else default_value for value in column]

# Assuming 'default_value' is the encoded value for 'unknown' category
default_value = -1  # You can choose an appropriate default value

new_df['weather_condition_encoded'] = safe_transform(encoder, new_df['weather_condition'], default_value)
new_df['road_condition_encoded'] = safe_transform(encoder, new_df['road_condition'], default_value)
new_df['lighting_condition_encoded'] = safe_transform(encoder, new_df['lighting_condition'], default_value)

# Assuming new_df is your new DataFrame with the categorical columns encoded

# Selecting the features to be scaled
new_features = new_df[['weather_condition_encoded', 'road_condition_encoded', 'lighting_condition_encoded', 'x', 'y']]

# Scaling the features
new_features_scaled = scaler.transform(new_features)  # Use the same scaler as used for the training data

# Making predictions with the scaled features
new_predictions = model.predict(new_features_scaled)
new_predicted_classes = new_predictions.argmax(axis=1)

# Convert the predicted classes to original labels if needed
original_labels = encoder.inverse_transform(new_predicted_classes)

print("Predicted Classes:", new_predicted_classes)
print("Original Labels:", original_labels)

# Making predictions
new_predictions = model.predict(new_features_scaled)
new_predicted_classes = new_predictions.argmax(axis=1)

# If you have the inverse mapping for your encoded target, you can convert predictions back to the original labels
# For example, if 'encoder' was used to encode your target variable:
original_labels = encoder.inverse_transform(new_predicted_classes)

print("Predicted Classes:", new_predicted_classes)
print("Original Labels:", original_labels)
