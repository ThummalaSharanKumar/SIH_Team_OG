import pandas as pd
import sqlite3

DB_FILE = 'mentors_eye.db'
CSV_FILE = 'project_student_data_historical.csv'

def migrate_csv_to_db():
    """
    Reads the historical student data from the CSV file and inserts it
    into the 'students' table in the SQLite database.
    This is a one-time operation.
    """
    try:
        df = pd.read_csv(CSV_FILE)
    except FileNotFoundError:
        print(f"FATAL ERROR: The source data file '{CSV_FILE}' was not found.")
        print("Please run 'generate_historical_data.py' first.")
        return

    try:
        conn = sqlite3.connect(DB_FILE)
        
        # Use the 'to_sql' method from pandas for an efficient bulk insert
        # 'if_exists='replace'' will drop the table if it exists and create a new one.
        # This is useful for re-running the migration during development.
        df.to_sql('students', conn, if_exists='replace', index=False)
        
        conn.close()
        
        print(f"Successfully migrated {len(df)} records from '{CSV_FILE}' to the 'students' table in '{DB_FILE}'.")
        print("The application will now read data from the database.")

    except sqlite3.Error as e:
        print(f"FATAL ERROR: An error occurred during database migration: {e}")

if __name__ == '__main__':
    migrate_csv_to_db()

