import pandas as pd
import numpy as np
from faker import Faker

# This script should be run once to create the historical dataset.
# It uses the 'project_student_data_enhanced.csv' as a base.

fake = Faker()

def generate_historical_trends(base_df):
    """
    Generates historical data points for each student based on their final 'Target' status.
    """
    historical_records = []
    
    for _, row in base_df.iterrows():
        # Create 4 data points for each student (e.g., representing 4 months)
        for period in range(1, 5):
            record = row.copy()
            record['ReportingPeriod'] = period
            
            # Simulate trends based on final outcome
            if record['Target'] == 'Dropout':
                # Trend downwards
                attendance_mod = -np.random.randint(3, 7) * (4 - period)
                score_mod = -np.random.uniform(2, 6) * (4 - period)
            elif record['Target'] == 'Graduate':
                # Trend upwards
                attendance_mod = np.random.randint(1, 3) * period
                score_mod = np.random.uniform(1, 4) * period
            else: # Enrolled
                # Fluctuate
                attendance_mod = np.random.randint(-3, 4)
                score_mod = np.random.uniform(-4, 5)

            # Apply modifications and ensure values stay within realistic bounds
            record['AttendancePercentage'] = max(40, min(100, row['AttendancePercentage'] + attendance_mod))
            record['AverageScore'] = round(max(30, min(100, row['AverageScore'] + score_mod)), 2)
            
            historical_records.append(record)
            
    return pd.DataFrame(historical_records)

if __name__ == "__main__":
    try:
        base_student_data = pd.read_csv('project_student_data_enhanced.csv')
        print("--- Base enhanced data loaded. ---")
    except FileNotFoundError:
        print("Error: 'project_student_data_enhanced.csv' not found.")
        print("Please run 'train_model.py' from the previous step first to generate it.")
        exit()

    print("--- Generating historical data for each student... ---")
    historical_df = generate_historical_trends(base_student_data)
    
    # Save the new historical dataset
    output_filename = 'project_student_data_historical.csv'
    historical_df.to_csv(output_filename, index=False)
    
    print(f"\nSuccessfully created historical data!")
    print(f"New file saved as: '{output_filename}'")
    print("\nHere's a preview of the data for one student:")
    print(historical_df[historical_df['StudentID'] == base_student_data['StudentID'].iloc[0]])
