import pandas as pd
import numpy as np
from faker import Faker
import os

# Initialize Faker to generate realistic names and contact info
fake = Faker('en_IN')

# --- Configuration ---
BASE_FILE = 'project_student_data.csv'
ENHANCED_HISTORICAL_OUTPUT_FILE = 'master_student_data_historical.csv'
WELLNESS_OUTPUT_FILE = 'student_wellness_survey.csv'

BRANCHES = ['Computer Science', 'Mechanical', 'Civil', 'Electronics', 'Electrical']
YEARS = [1, 2, 3, 4]
NUM_PERIODS = 4

def generate_holistic_data():
    """
    Orchestrates the entire data generation process.
    1. Reads base data.
    2. Adds demographics including Name, Branch, Year, EMAIL, and PHONE.
    3. Generates wellness survey data.
    4. Creates a comprehensive historical dataset by merging all data.
    """
    print("--- Starting Data Enrichment (with Email/Phone fix) ---")

    try:
        base_df = pd.read_csv(BASE_FILE)
    except FileNotFoundError:
        print(f"FATAL ERROR: Base data file '{BASE_FILE}' not found.")
        return

    # --- 1. Augment with Demographics & Contact Info ---
    print(f"Step 1: Augmenting {len(base_df)} students with full demographics...")
    
    names = [fake.name() for _ in range(len(base_df))]
    base_df['Name'] = names
    
    # --- FIX: Generate and add Email and Phone columns ---
    # Create email based on the first part of the name to make it look realistic
    base_df['Email'] = [f"{name.split(' ')[0].lower()}{np.random.randint(10,99)}@college.edu" for name in names]
    base_df['Phone'] = [fake.phone_number() for _ in range(len(base_df))]

    base_df['Branch'] = np.random.choice(BRANCHES, len(base_df), p=[0.3, 0.2, 0.2, 0.2, 0.1])
    base_df['Year'] = np.random.choice(YEARS, len(base_df), p=[0.4, 0.3, 0.2, 0.1])
    print("-> Added Name, Email, Phone, Branch, and Year columns.")

    # --- 2. Generate Wellness Survey Data ---
    print(f"Step 2: Generating wellness survey data...")
    wellness_data = []
    for _, row in base_df.iterrows():
        if row['Target'] == 'Dropout':
            financial_stress = np.random.randint(3, 6)
            health_impact = np.random.choice(['Yes', 'No'], p=[0.6, 0.4])
            career_confidence = np.random.randint(1, 4)
        elif row['Target'] == 'Graduate':
            financial_stress = np.random.randint(1, 4)
            health_impact = np.random.choice(['Yes', 'No'], p=[0.1, 0.9])
            career_confidence = np.random.randint(4, 6)
        else: # Enrolled
            financial_stress = np.random.randint(1, 5)
            health_impact = np.random.choice(['Yes', 'No'], p=[0.3, 0.7])
            career_confidence = np.random.randint(3, 6)
            
        wellness_data.append({
            'StudentID': row['StudentID'],
            'FinancialStressScore': financial_stress,
            'HealthImpact': health_impact,
            'CareerConfidenceScore': career_confidence
        })

    wellness_df = pd.DataFrame(wellness_data)
    wellness_df.to_csv(WELLNESS_OUTPUT_FILE, index=False)
    print(f"-> Saved wellness data to '{WELLNESS_OUTPUT_FILE}'.")

    # --- 3. Create Comprehensive Historical Dataset ---
    print("Step 3: Generating historical data and creating the master file...")
    merged_df = pd.merge(base_df, wellness_df, on='StudentID')
    
    historical_df_list = []
    for _, row in merged_df.iterrows():
        for period in range(1, NUM_PERIODS + 1):
            historical_row = row.copy()
            historical_row['ReportingPeriod'] = period
            
            if period < NUM_PERIODS:
                historical_row['AttendancePercentage'] = max(40, row['AttendancePercentage'] + np.random.randint(-5, 5) * (NUM_PERIODS - period))
                historical_row['AverageScore'] = max(30, round(row['AverageScore'] + np.random.uniform(-3, 3) * (NUM_PERIODS - period), 2))
            
            historical_df_list.append(historical_row)
    
    final_historical_df = pd.DataFrame(historical_df_list)
    final_historical_df.to_csv(ENHANCED_HISTORICAL_OUTPUT_FILE, index=False)
    print(f"-> Saved master historical data to '{ENHANCED_HISTORICAL_OUTPUT_FILE}'.")
    print("\n--- Data Generation Fix Complete ---")
    print("Next, please re-run the setup pipeline: train_model.py, then migrate_data.py.")

if __name__ == '__main__':
    generate_holistic_data()

