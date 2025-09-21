import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt
import joblib

# --- 1. Load Data ---
try:
    # Use the dataset with 300 students for more robust training
    df = pd.read_csv('project_student_data.csv')
except FileNotFoundError:
    print("Error: 'project_student_data.csv' not found.")
    print("Please ensure the CSV file is in the same directory as this script.")
    # Exit if the file doesn't exist, as training would be meaningless
    exit()

print("--- Data Loaded Successfully ---")
print("Original Data Head:")
print(df.head())
print("\n")


# --- 2. Feature Engineering ---
print("--- Performing Feature Engineering ---")
# Create 'Grade_Velocity' feature (change from midterm to current average)
df['Grade_Velocity'] = df['AverageScore'] - df['MidtermGrade']

# Create a simple 'Engagement_Score'
df['Engagement_Score'] = df['AttendancePercentage'] * df['LMS_Logins_Per_Week']
print("New Features ('Grade_Velocity', 'Engagement_Score') Created.\n")


# --- 3. Preprocessing ---
print("--- Preprocessing Data ---")
# One-Hot Encode 'FeeStatus'
df = pd.get_dummies(df, columns=['FeeStatus'], drop_first=True)
print("Categorical feature 'FeeStatus' has been One-Hot Encoded.")

# Label Encode the Target variable
le = LabelEncoder()
df['Target_Encoded'] = le.fit_transform(df['Target'])
print("Target variable has been Label Encoded.")

# Keep a mapping of encoded labels to original class names for later
class_names = le.classes_
print(f"Label mapping: { {i: label for i, label in enumerate(class_names)} }\n")

# Separate features (X) and target (y)
y = df['Target_Encoded']
X = df.drop(columns=['StudentID', 'Target', 'Target_Encoded'])

# Scale numerical features
print("--- Scaling Numerical Features ---")
# IMPORTANT: Save the scaler so we can use the *same* scaling on new data
scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(X)
X = pd.DataFrame(X_scaled, columns=X.columns)
print("Numerical features have been scaled.\n")


# --- 4. Data Splitting ---
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42, stratify=y
)
print(f"--- Data Split into Training ({len(X_train)} rows) and Testing ({len(X_test)} rows) Sets ---\n")


# --- 5. Model Training ---
print("--- Training Random Forest Model ---")
# These are reasonable starting hyperparameters
model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10, min_samples_leaf=2)
model.fit(X_train, y_train)
print("Model training complete.\n")


# --- 6. Model Evaluation ---
print("--- Evaluating Model Performance ---")
predictions = model.predict(X_test)
accuracy = accuracy_score(y_test, predictions)
print(f"Model Accuracy: {accuracy * 100:.2f}%\n")

# Classification Report (Precision, Recall, F1-Score)
print("Classification Report:")
print(classification_report(y_test, predictions, target_names=class_names))

# Confusion Matrix Visualization
print("Confusion Matrix:")
cm = confusion_matrix(y_test, predictions)
plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=class_names, yticklabels=class_names)
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.title('Confusion Matrix')
# Save the plot to a file
plt.savefig('confusion_matrix.png')
print("Confusion matrix plot saved as 'confusion_matrix.png'\n")


# --- 7. Feature Importance ---
print("--- Analyzing Feature Importance ---")
feature_importances = pd.DataFrame(model.feature_importances_,
                                   index = X_train.columns,
                                   columns=['importance']).sort_values('importance', ascending=False)
print("Top 10 Most Important Features:")
print(feature_importances.head(10))
print("\n")


# --- 8. Save Model and Processors for Deployment ---
print("--- Saving Model and Supporting Files ---")
# Save the trained model
joblib.dump(model, 'student_dropout_model.joblib')
# Save the scaler
joblib.dump(scaler, 'scaler.joblib')
# Save the label encoder
joblib.dump(le, 'label_encoder.joblib')
# Save the column order (very important!)
model_columns = list(X.columns)
joblib.dump(model_columns, 'model_columns.joblib')

print("The following files have been saved and are ready for the dashboard:")
print("- student_dropout_model.joblib (The trained model)")
print("- scaler.joblib (The feature scaler)")
print("- label_encoder.joblib (The target variable encoder)")
print("- model_columns.joblib (The exact column order the model expects)")