import joblib
import pandas as pd
import numpy as np

# --- Load all the model artifacts ---
try:
    model = joblib.load('student_dropout_model.joblib')
    scaler = joblib.load('scaler.joblib')
    le = joblib.load('label_encoder.joblib')
    model_columns = joblib.load('model_columns.joblib')
except FileNotFoundError as e:
    print(f"🛑 FATAL ERROR: Could not load model artifacts. Make sure these files are in the root directory: {e}")
    model = scaler = le = model_columns = None

def get_risk_profile(student_data):
    """
    Takes a dictionary of student data, preprocesses it, and returns a
    full risk profile including level, score, probabilities, and contributing factors.
    """
    if not all([model, scaler, le, model_columns]):
        return {
            "level": "Error", "score": 0,
            "probabilities": {}, "factors": [{"text": "Model not loaded", "importance": 1}]
        }

    # --- 1. Preprocess the incoming data ---
    # Create a DataFrame from the single student dictionary
    df = pd.DataFrame([student_data])

    # Feature Engineering (must match training script)
    df['Grade_Velocity'] = df['AverageScore'] - df['MidtermGrade']
    df['Engagement_Score'] = df['AttendancePercentage'] * df['LMS_Logins_Per_Week']

    # One-Hot Encode FeeStatus
    for col in ['FeeStatus_Overdue', 'FeeStatus_Paid']:
        if col not in df.columns:
            df[col] = 0 # Add missing columns if not present in this student's data
    if 'FeeStatus' in df.columns:
        if df.loc[0, 'FeeStatus'] == 'Overdue':
            df.loc[0, 'FeeStatus_Overdue'] = 1
        elif df.loc[0, 'FeeStatus'] == 'Paid':
            df.loc[0, 'FeeStatus_Paid'] = 1
    
    # Ensure all required model columns are present and in the correct order
    df_processed = pd.DataFrame(columns=model_columns)
    df_processed = pd.concat([df_processed, df], ignore_index=True, sort=False).fillna(0)
    df_processed = df_processed[model_columns]

    # Scaling (use the loaded scaler)
    df_scaled = scaler.transform(df_processed)

    # --- 2. Make Prediction ---
    probabilities = model.predict_proba(df_scaled)[0]
    prediction_encoded = np.argmax(probabilities)
    predicted_class = le.inverse_transform([prediction_encoded])[0]
    
    # --- 3. Determine Risk Level, Score, and Factors ---
    score = 0
    factors = []
    
    # Define thresholds and corresponding factors
    # These rules provide a transparent layer on top of the ML prediction
    if student_data.get('AttendancePercentage', 100) < 75:
        score += 25
        factors.append({"text": "Low Attendance", "importance": 0.8})
        
    if student_data.get('AverageScore', 100) < 60:
        score += 25
        factors.append({"text": "Low Average Score", "importance": 0.9})

    if student_data.get('FeeStatus') == 'Overdue':
        score += 20
        factors.append({"text": "Overdue Fees", "importance": 0.7})
        
    grade_velocity = student_data.get('AverageScore', 0) - student_data.get('MidtermGrade', 0)
    if grade_velocity < -10:
        score += 30
        factors.append({"text": "Declining Grades", "importance": 1.0})

    # Determine risk level based on the calculated score
    if score >= 60:
        level = "High"
    elif score >= 30:
        level = "Medium"
    else:
        level = "Low"

    # If the score is low but the model predicts Dropout, elevate risk
    if level == "Low" and predicted_class == "Dropout":
        level = "Medium"
        score = max(score, 40) # Give it a medium score
        if not factors: # Add a generic factor if none exist
             factors.append({"text": "At-Risk Pattern Detected", "importance": 0.6})


    # Sort factors by importance for the UI
    factors.sort(key=lambda x: x['importance'], reverse=True)

    # Format probabilities for the UI
    prob_dict = {le.classes_[i]: round(p * 100) for i, p in enumerate(probabilities)}

    return {
        "level": level,
        "score": score,
        "probabilities": prob_dict,
        "factors": factors
    }

