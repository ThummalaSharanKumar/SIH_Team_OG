import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib
from faker import Faker # Library to generate fake data

# Initialize Faker to generate mock data
fake = Faker()

# --- 1. Load Original Data ---
try:
    df = pd.read_csv('project_student_data.csv')
    print("--- Original Data Loaded Successfully ---")
except FileNotFoundError:
    print("Error: 'project_student_data.csv' not found. Please ensure it's in the directory.")
    exit()

# --- 2. Enhance Dataset with New Columns ---
print("--- Enhancing Dataset with Email and Phone ---")
# Generate a list of unique emails and phone numbers
emails = [fake.email() for _ in range(len(df))]
phones = [fake.phone_number() for _ in range(len(df))]
df['Email'] = emails
df['Phone'] = phones

# Save the newly enhanced dataframe to a new file
df.to_csv('project_student_data_enhanced.csv', index=False)
print("Enhanced data saved to 'project_student_data_enhanced.csv'\n")


# --- 3. Feature Engineering ---
print("--- Performing Feature Engineering ---")
df['Grade_Velocity'] = df['AverageScore'] - df['MidtermGrade']
df['Engagement_Score'] = df['AttendancePercentage'] * df['LMS_Logins_Per_Week']
print("New features created.\n")


# --- 4. Preprocessing ---
print("--- Preprocessing Data ---")
# Drop non-feature columns before processing
df_features = df.drop(columns=['StudentID', 'Email', 'Phone', 'Target'])

df_features = pd.get_dummies(df_features, columns=['FeeStatus'], drop_first=True)

y = df['Target'] # Use original target for encoding
le = LabelEncoder()
y_encoded = le.fit_transform(y)

# Get the column order before scaling, after dummification
feature_columns = df_features.columns.tolist()

# Ensure all expected dummy columns are present, even if not in the source data
# This handles cases where a category might be missing in a subset of data
expected_dummies = ['FeeStatus_Overdue', 'FeeStatus_Paid']
for col in expected_dummies:
    if col not in feature_columns:
        df_features[col] = 0

# Reorder to ensure consistency
df_features = df_features[feature_columns]


scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(df_features)
X = pd.DataFrame(X_scaled, columns=feature_columns)
print("Preprocessing complete.\n")


# --- 5. Data Splitting ---
X_train, X_test, y_train, y_test = train_test_split(
    X, y_encoded, test_size=0.3, random_state=42, stratify=y_encoded
)
print(f"--- Data Split into Training ({len(X_train)} rows) and Testing ({len(X_test)} rows) Sets ---\n")


# --- 6. Model Training ---
print("--- Training Random Forest Model ---")
model = RandomForestClassifier(n_estimators=150, random_state=42, max_depth=12, min_samples_leaf=3, class_weight='balanced')
model.fit(X_train, y_train)
print("Model training complete.\n")


# --- 7. Model Evaluation ---
print("--- Evaluating Model Performance ---")
predictions = model.predict(X_test)
accuracy = accuracy_score(y_test, predictions)
class_names = le.classes_
print(f"Model Accuracy: {accuracy * 100:.2f}%\n")
print("Classification Report:")
print(classification_report(y_test, predictions, target_names=class_names))


# --- 8. Save Model and Processors ---
print("--- Saving Model and Supporting Files ---")
joblib.dump(model, 'student_dropout_model.joblib')
joblib.dump(scaler, 'scaler.joblib')
joblib.dump(le, 'label_encoder.joblib')
joblib.dump(feature_columns, 'model_columns.joblib')

print("Model and supporting files have been saved successfully.")

