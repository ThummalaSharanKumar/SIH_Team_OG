import pandas as pd
import sqlite3
import os

# --- Configuration ---
# This script reads from the master data file we created.
DATA_FILE = 'master_student_data_historical.csv'
DB_FILE = 'mentors_eye.db'

def migrate_data_to_db():
    """
    Reads the comprehensive historical student data from the CSV
    and populates the 'students' table in the SQLite database.
    This is a one-time operation to set up the application's data source.
    """
    if not os.path.exists(DATA_FILE):
        print(f"FATAL ERROR: Data file '{DATA_FILE}' not found.")
        print("Please ensure you have run 'generate_master_data.py' successfully.")
        return

    if not os.path.exists(DB_FILE):
        print(f"FATAL ERROR: Database file '{DB_FILE}' not found.")
        print("Please run 'database_setup.py' first.")
        return

    print(f"--- Starting data migration from '{DATA_FILE}' to '{DB_FILE}' ---")
    
    df = pd.read_csv(DATA_FILE)
    
    # Establish connection to the database
    conn = sqlite3.connect(DB_FILE)
    
    # Use pandas' to_sql function for an efficient bulk insert.
    # 'if_exists='replace'' will drop the table if it already exists and create a new one.
    # This ensures a clean slate every time you run the setup.
    df.to_sql('students', conn, if_exists='replace', index=False)
    
    # Verify the migration by counting the inserted rows
    count = pd.read_sql('SELECT COUNT(*) FROM students', conn).iloc[0, 0]
    
    conn.close()
    
    print(f"-> Successfully migrated {count} records into the 'students' table.")
    print("--- Data Migration Complete ---")
    print("Next, you can run the final application with 'python app.py'.")

if __name__ == '__main__':
    migrate_data_to_db()

