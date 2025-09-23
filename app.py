import pandas as pd
import joblib
from flask import Flask, jsonify, render_template, request, session, redirect, url_for
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3
import os

# Import the final prediction function
from predict import get_holistic_risk_profile

app = Flask(__name__)
app.secret_key = 'a_very_secret_key_for_production'

# --- File Configuration ---
MODEL_FILE = 'student_dropout_model.joblib'
LABEL_ENCODER_FILE = 'label_encoder.joblib'
DB_FILE = 'mentors_eye.db'

# --- Load Model Artifacts ---
# These are loaded once when the application starts.
try:
    model = joblib.load(MODEL_FILE)
    label_encoder = joblib.load(LABEL_ENCODER_FILE)
    print("--- Model and label encoder loaded successfully. ---")
except FileNotFoundError as e:
    print(f"🛑 FATAL ERROR: Could not load model files: {e}")
    print("Please ensure you have run 'train_model.py' successfully.")
    model, label_encoder = None, None

# --- In-memory User Store (for demonstration) ---
USERS = {
    "mentor@college.edu": generate_password_hash("password123")
}

# --- Helper Function ---
def get_db_connection():
    """Establishes a connection to the SQLite database."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

# --- Routes ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        if email in USERS and check_password_hash(USERS.get(email), password):
            session['user_email'] = email
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error="Invalid credentials. Please try again.")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_email', None)
    return redirect(url_for('login'))

@app.route('/')
def dashboard():
    if 'user_email' not in session:
        return redirect(url_for('login'))
        
    if model is None or label_encoder is None:
        return "Error: Model artifacts not loaded. Please check server logs.", 500

    conn = get_db_connection()
    # Fetch only the latest record for each student for the main list
    query = """
    SELECT t1.*
    FROM students t1
    INNER JOIN (
        SELECT StudentID, MAX(ReportingPeriod) as MaxPeriod
        FROM students
        GROUP BY StudentID
    ) t2 ON t1.StudentID = t2.StudentID AND t1.ReportingPeriod = t2.MaxPeriod
    """
    latest_df = pd.read_sql_query(query, conn)
    conn.close()

    student_data_with_risk = []
    for _, row in latest_df.iterrows():
        student_profile_for_prediction = row.drop(['StudentID', 'Name', 'Email', 'Phone', 'Target', 'ReportingPeriod'])
        student_profile_df = pd.DataFrame([student_profile_for_prediction])
        
        risk_profile = get_holistic_risk_profile(student_profile_df, model, label_encoder)
        
        student_display_data = row.to_dict()
        student_display_data['risk'] = risk_profile
        student_data_with_risk.append(student_display_data)

    return render_template('index.html', student_data=student_data_with_risk, user_email=session.get('user_email'))

@app.route('/student/<student_id>')
def get_student_details(student_id):
    if 'user_email' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    conn = get_db_connection()
    student_history_df = pd.read_sql_query(f"SELECT * FROM students WHERE StudentID = '{student_id}' ORDER BY ReportingPeriod", conn)
    conn.close()
    
    if student_history_df.empty:
        return jsonify({"error": "Student not found"}), 404
        
    student_history = student_history_df.to_dict('records')
    latest_record = student_history[-1]
    
    latest_record_for_prediction = pd.DataFrame([latest_record]).drop(columns=['StudentID', 'Name', 'Email', 'Phone', 'Target', 'ReportingPeriod'])
    
    risk_profile = get_holistic_risk_profile(latest_record_for_prediction, model, label_encoder)
    
    response_data = {
        **latest_record,
        "risk": risk_profile,
        "history": student_history
    }
    return jsonify(response_data)

# --- Note Taking API Endpoints ---
@app.route('/add_note', methods=['POST'])
def add_note():
    if 'user_email' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    data = request.json
    try:
        conn = get_db_connection()
        conn.execute('INSERT INTO notes (student_id, mentor_name, note_text) VALUES (?, ?, ?)',
                     (data['student_id'], data['mentor_name'], data['note_text']))
        conn.commit()
        conn.close()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/get_notes/<student_id>')
def get_notes(student_id):
    if 'user_email' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    try:
        conn = get_db_connection()
        notes_cursor = conn.execute('SELECT * FROM notes WHERE student_id = ? ORDER BY timestamp DESC', (student_id,))
        notes = [dict(row) for row in notes_cursor.fetchall()]
        conn.close()
        return jsonify(notes)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    if not os.path.exists(DB_FILE):
        print(f"🛑 FATAL ERROR: Database file '{DB_FILE}' not found. Please run 'database_setup.py' and 'migrate_data.py' first.")
    elif model is None:
         print(f"🛑 FATAL ERROR: Model not loaded. Please ensure '{MODEL_FILE}' exists.")
    else:
        app.run(debug=True)

