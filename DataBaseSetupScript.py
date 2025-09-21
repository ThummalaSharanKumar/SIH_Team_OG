import sqlite3
import os

DB_FILE = 'mentors_eye.db'

def setup_database():
    """
    Sets up the SQLite database and creates the 'notes' table if it doesn't exist.
    This script should be run once to initialize the database.
    """
    if os.path.exists(DB_FILE):
        print(f"Database file '{DB_FILE}' already exists. Setup not required.")
        return

    print(f"Creating new database file: {DB_FILE}")
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # Create the 'notes' table
        # student_id will link to the StudentID from our CSV
        # timestamp will record when the note was created
        cursor.execute('''
            CREATE TABLE notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                mentor_name TEXT NOT NULL,
                note_text TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        print("Table 'notes' created successfully.")
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")

if __name__ == '__main__':
    setup_database()
