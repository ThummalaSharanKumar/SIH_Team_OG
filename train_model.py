import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, MinMaxScaler, OneHotEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import joblib
import os

# --- Configuration ---
DATA_FILE = 'master_student_data_historical.csv'
MODEL_FILE = 'student_dropout_model.joblib'

def train_holistic_model():
    """
    Trains the advanced model using the full master dataset.
    1. Loads the comprehensive historical data.
    2. Uses only the LATEST record for each student for training the prediction model.
    3. Preprocesses academic, demographic, and wellness features.
    4. Trains, evaluates, and saves the new, more powerful model.
    """
    print("--- Starting Advanced Modeling & Re-Training ---")

    try:
        df = pd.read_csv(DATA_FILE)
    except FileNotFoundError:
        print(f"FATAL ERROR: Master data file '{DATA_FILE}' not found.")
        print("Please run 'generate_master_data.py' first to create it.")
        return

    # --- 1. Select Latest Records for Training ---
    print("Step 1: Selecting the most recent data for each student for training...")
    latest_df = df.loc[df.groupby('StudentID')['ReportingPeriod'].idxmax()]
    print(f"-> Using {len(latest_df)} unique student records for training.")

    # --- 2. Feature Engineering & Preprocessing Setup ---
    print("Step 2: Setting up preprocessing for the holistic dataset...")
    
    # Define the target variable
    y_raw = latest_df['Target']
    
    # Define features (X) by dropping identifiers and the target variable
    # This now correctly handles the presence of Email and Phone.
    X = latest_df.drop(columns=[
        'StudentID', 'Name', 'Email', 'Phone', 'Target', 
        'ReportingPeriod', 'MidtermGrade'
    ])

    # Label Encode the target variable
    le = LabelEncoder()
    y = le.fit_transform(y_raw)
    class_names = le.classes_
    print(f"-> Target variable encoded. Mapping: { {i: label for i, label in enumerate(class_names)} }")

    # Define which columns are numerical and which are categorical
    numerical_features = X.select_dtypes(include=np.number).columns.tolist()
    categorical_features = ['Branch', 'HealthImpact', 'FeeStatus']
    
    print(f"-> Identified Numerical Features: {numerical_features}")
    print(f"-> Identified Categorical Features: {categorical_features}")

    # Create a robust preprocessing pipeline
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', MinMaxScaler(), numerical_features),
            ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
        ],
        remainder='passthrough'
    )

    # --- 3. Model Training ---
    print("Step 3: Training the new Random Forest model pipeline...")
    model_pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('classifier', RandomForestClassifier(n_estimators=150, random_state=42, max_depth=15, min_samples_leaf=3))
    ])

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)
    
    model_pipeline.fit(X_train, y_train)
    print("-> Model training complete.")

    # --- 4. Model Evaluation ---
    print("Step 4: Evaluating the new holistic model...")
    predictions = model_pipeline.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)
    
    print(f"\nModel Accuracy: {accuracy * 100:.2f}%\n")
    print("Classification Report:")
    print(classification_report(y_test, predictions, target_names=class_names))
    
    # --- 5. Analyze New Feature Importance ---
    print("Step 5: Analyzing feature importance...")
    try:
        ohe_feature_names = model_pipeline.named_steps['preprocessor'].named_transformers_['cat'].get_feature_names_out(categorical_features)
        all_feature_names = numerical_features + list(ohe_feature_names)
        
        importances = model_pipeline.named_steps['classifier'].feature_importances_
        feature_importance_df = pd.DataFrame({'feature': all_feature_names, 'importance': importances})
        feature_importance_df = feature_importance_df.sort_values('importance', ascending=False)
        
        print("Top 10 Most Important Features:")
        print(feature_importance_df.head(10))
    except Exception as e:
        print(f"Could not calculate feature importances: {e}")

    # --- 6. Save the Model and Processors ---
    print("\nStep 6: Saving the new model pipeline...")
    joblib.dump(model_pipeline, MODEL_FILE)
    joblib.dump(le, 'label_encoder.joblib')
    print(f"-> New model pipeline saved to '{MODEL_FILE}'.")
    print("-> Label encoder saved to 'label_encoder.joblib'.")
    print("\n--- Model re-training complete. ---")
    print("Next, please run 'migrate_data.py' to update your database.")

if __name__ == '__main__':
    train_holistic_model()

