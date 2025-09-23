import joblib
import pandas as pd
import numpy as np

# --- Configuration ---
# These thresholds define what constitutes a "risk factor". They can be adjusted.
ATTENDANCE_THRESHOLD = 75
SCORE_THRESHOLD = 60
FINANCIAL_STRESS_THRESHOLD = 4 # High risk if score is 4 or 5
CAREER_CONFIDENCE_THRESHOLD = 2 # High risk if score is 1 or 2

def get_holistic_risk_profile(student_data, model, label_encoder):
    """
    Calculates a student's risk profile using the holistic model pipeline.
    Also determines the specific factors that contributed to the risk.

    Args:
        student_data (pd.DataFrame): A DataFrame with a single row of student data.
        model (Pipeline): The trained scikit-learn pipeline.
        label_encoder (LabelEncoder): The fitted label encoder for the target.

    Returns:
        dict: A dictionary containing the risk level, probabilities, and a list of factors.
    """
    # Predict the probability for each class
    probabilities = model.predict_proba(student_data)[0]
    
    # Get the predicted class index
    prediction_index = model.predict(student_data)[0]
    risk_level = label_encoder.inverse_transform([prediction_index])[0]

    # Map probabilities to class names
    prob_dict = {label: round(prob, 2) for label, prob in zip(label_encoder.classes_, probabilities)}

    # --- Determine Risk Factors ---
    factors = []
    student = student_data.iloc[0] # Get the student's data as a Series

    if student['AttendancePercentage'] < ATTENDANCE_THRESHOLD:
        factors.append({'text': 'Low Attendance'})
        
    if student['AverageScore'] < SCORE_THRESHOLD:
        factors.append({'text': 'Low Average Score'})

    if student['FeeStatus'] == 'Overdue':
        factors.append({'text': 'Overdue Fees'})
        
    if student['FinancialStressScore'] >= FINANCIAL_STRESS_THRESHOLD:
        factors.append({'text': 'High Financial Stress'})

    if student['HealthImpact'] == 'Yes':
        factors.append({'text': 'Health Issues Impacting Study'})

    if student['CareerConfidenceScore'] <= CAREER_CONFIDENCE_THRESHOLD:
        factors.append({'text': 'Low Career Confidence'})

    return {
        'level': risk_level,
        'probabilities': prob_dict,
        'factors': factors
    }

