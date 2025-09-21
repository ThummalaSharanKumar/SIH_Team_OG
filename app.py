from flask import Flask, render_template, jsonify, request, redirect, url_for, flash, session
from predict import get_risk_profile
import sqlite3
import os

app = Flask(__name__)
# A secret key is required for session management
app.secret_key = os.urandom(24) 
DB_FILE = 'mentors_eye.db'

# --- In a real application, users would be stored in a database ---
USERS = {
    "mentor@college.edu": "password123",
    "admin@college.edu": "adminpass"
}

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    try:
        conn = sqlite3.connect(DB_FILE)
        # This allows you to access columns by name (like a dictionary)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"FATAL ERROR: Could not connect to database '{DB_FILE}': {e}")
        return None

# --- AUTHENTICATION ROUTES ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handles the login process."""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if email in USERS and USERS[email] == password:
            session['logged_in'] = True
            session['email'] = email
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials. Please try again.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logs the user out."""
    session.clear()
    flash('You were successfully logged out', 'success')
    return redirect(url_for('login'))


# --- PROTECTED DASHBOARD ROUTE ---

@app.route('/')
def dashboard():
    """Main dashboard, now powered by the SQLite database."""
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    if conn is None:
        return "Error: Database connection failed.", 500
        
    try:
        # SQL query to get the latest record for each student
        query = """
            SELECT s.*
            FROM students s
            INNER JOIN (
                SELECT StudentID, MAX(ReportingPeriod) as MaxPeriod
                FROM students
                GROUP BY StudentID
            ) sm ON s.StudentID = sm.StudentID AND s.ReportingPeriod = sm.MaxPeriod;
        """
        latest_student_records = conn.execute(query).fetchall()
        conn.close()
    except sqlite3.OperationalError:
         return "Error: The 'students' table was not found. Please run the `migrate_data.py` script first.", 500

    students_with_risk = []
    for row in latest_student_records:
        student = dict(row) # Convert the database row to a dictionary
        risk_profile = get_risk_profile(student) 
        students_with_risk.append({**student, "risk": risk_profile})
    
    students_with_risk.sort(key=lambda x: x['risk']['score'], reverse=True)
    return render_template('index.html', student_data=students_with_risk, user_email=session.get('email'))


# --- API ENDPOINTS ---

@app.route('/student/<student_id>')
def get_student_details(student_id):
    if not session.get('logged_in'): return jsonify({"error": "Unauthorized"}), 401
    
    conn = get_db_connection()
    if conn is None: return jsonify({"error": "Database connection failed."}), 500
    
    # Query for the full history of the student
    student_history_records = conn.execute(
        'SELECT * FROM students WHERE StudentID = ? ORDER BY ReportingPeriod', (student_id,)
    ).fetchall()
    
    if not student_history_records:
        conn.close()
        return jsonify({"error": "Student not found"}), 404
        
    # The last record is the most current one
    current_student_data = dict(student_history_records[-1])
    risk_profile = get_risk_profile(current_student_data) 
    
    # Prepare history for the chart, converting rows to dictionaries
    history_for_chart = [dict(row) for row in student_history_records]
    conn.close()
    
    response_data = {**current_student_data, "risk": risk_profile, "history": history_for_chart}
    return jsonify(response_data)

@app.route('/recalculate_risk', methods=['POST'])
def recalculate_risk():
    if not session.get('logged_in'): return jsonify({"error": "Unauthorized"}), 401
    student_data = request.json
    if not student_data: return jsonify({"error": "Invalid data provided"}), 400
    risk_profile = get_risk_profile(student_data)
    return jsonify(risk_profile)

@app.route('/get_notes/<student_id>')
def get_notes(student_id):
    if not session.get('logged_in'): return jsonify({"error": "Unauthorized"}), 401
    conn = get_db_connection()
    if conn is None: return jsonify({"error": "Database connection failed."}), 500
    notes = conn.execute('SELECT * FROM notes WHERE student_id = ? ORDER BY timestamp DESC', (student_id,)).fetchall()
    conn.close()
    return jsonify([dict(note) for note in notes])

@app.route('/add_note', methods=['POST'])
def add_note():
    if not session.get('logged_in'): return jsonify({"error": "Unauthorized"}), 401
    note_data = request.json
    student_id = note_data.get('student_id')
    mentor_name = session.get('email', 'Mentor')
    note_text = note_data.get('note_text')

    if not all([student_id, mentor_name, note_text]):
        return jsonify({"error": "Missing data for note"}), 400

    conn = get_db_connection()
    if conn is None: return jsonify({"error": "Database connection failed."}), 500
    conn.execute('INSERT INTO notes (student_id, mentor_name, note_text) VALUES (?, ?, ?)',
                 (student_id, mentor_name, note_text))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "Note added successfully."})

if __name__ == '__main__':
    # Ensure the database file exists before running the app
    if not os.path.exists(DB_FILE):
        print(f"WARNING: The database file '{DB_FILE}' does not exist.")
        print("Please run 'database_setup.py' and 'migrate_data.py' first.")
    app.run(debug=True)

