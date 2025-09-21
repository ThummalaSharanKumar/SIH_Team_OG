import sqlite3

DB_FILE = 'mentors_eye.db'

def create_tables():
    """
    Sets up the database tables. This should be run once.
    This new version includes a 'students' table for all student data.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # --- Students Table ---
    # This table will store all historical data for each student
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            StudentID TEXT NOT NULL,
            ReportingPeriod INTEGER NOT NULL,
            AttendancePercentage INTEGER,
            AverageScore REAL,
            FeeStatus TEXT,
            LMS_Logins_Per_Week INTEGER,
            MidtermGrade REAL,
            ScholarshipHolder INTEGER,
            Target TEXT,
            Email TEXT,
            Phone TEXT,
            UNIQUE(StudentID, ReportingPeriod) -- Ensures no duplicate records for the same period
        );
    ''')

    # --- Notes Table (unchanged) ---
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            mentor_name TEXT NOT NULL,
            note_text TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    ''')

    conn.commit()
    conn.close()
    print(f"Database '{DB_FILE}' and tables ('students', 'notes') are set up successfully.")

if __name__ == '__main__':
    create_tables()

