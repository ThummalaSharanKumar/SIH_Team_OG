# SIH_Team_OG
This project builds an AI-driven system to predict student dropout risk using data like attendance, grades, engagement, and fee status. With feature engineering, a Random Forest model, and visual insights, it highlights at-risk students early, enabling educators to take proactive, data-driven interventions.


Mentor's Eye: A Holistic AI-Powered Student Success Platform
🚀 Project Overview
Mentor's Eye is a comprehensive web application designed to help educational institutions proactively identify students at risk of dropping out. Moving beyond traditional metrics, this platform integrates academic data, behavioral patterns, and self-reported wellness indicators to create a holistic "whole student" profile.

The system uses a machine learning model to predict risk and presents the insights on an intuitive, interactive dashboard. This empowers mentors and counselors to intervene early, effectively, and with the right context, providing targeted support where it's needed most.

✨ Key Features
Holistic Risk Prediction: Utilizes a Random Forest model trained on academic, demographic, and wellness data (financial stress, health, career confidence) for a nuanced understanding of student risk.

Interactive Dashboard: A clean, user-friendly interface for viewing all students, sorted and color-coded by their predicted risk level (High, Medium, Low).

Detailed Student Profiles: A comprehensive drill-down view for each student, showcasing their full academic, demographic, and wellness profile.

Dynamic Intervention Playbook: An intelligent, context-aware playbook that suggests specific, actionable interventions based on the reasons for a student's risk.

Historical Trend Analysis: Visualizes key metrics like attendance and grades over time with line charts, helping mentors spot crucial trends.

Mentor Notes & Logging: A persistent logging system that allows mentors to record interactions and track a student's progress directly within the application, backed by a database.

Secure User Authentication: A complete login system ensures that only authorized personnel can access sensitive student data.

🛠️ Tech Stack
Backend: Python, Flask

Database: SQLite

Machine Learning: Scikit-learn, Pandas, NumPy

Frontend: HTML, Tailwind CSS, JavaScript

Data Visualization: Chart.js

⚙️ Setup and Execution Guide
Follow these instructions to set up and run the application on a new system.

1. Prerequisites
Python 3.8 or higher

pip (Python package installer)

2. Initial Setup
Clone the repository or ensure all project files are in a single directory.

a. Create and Activate a Virtual Environment (Recommended)

Open your terminal or command prompt in the project directory and run:

# Create the virtual environment
python -m venv .venv

# Activate on Windows
.venv\Scripts\activate

# Activate on Mac/Linux
source .venv/bin/activate

b. Install Dependencies

Use the provided requirements.txt file to install all necessary libraries with a single command:

pip install -r requirements.txt

3. One-Time Data & Model Pipeline Execution
You must run the following scripts in this exact order. They will create the database, generate the complete dataset, train the model, and populate the database.

a. Setup the Database
This creates the mentors_eye.db file with the required tables.

python database_setup.py

b. Generate the Master Dataset
This creates the master_student_data_historical.csv file.

python generate_master_data.py

c. Train the Machine Learning Model
This trains the model and creates the necessary .joblib files.

python train_model.py

d. Migrate Data to the Database
This populates the database with the data from the master CSV.

python migrate_data.py

4. Run the Application
Once the one-time setup is complete, you can start the Flask web server with this command:

python app.py

5. Access the Dashboard
Open your web browser and navigate to the following address:

http://127.0.0.1:5000

You will be directed to the login page. Use the following credentials to access the dashboard:

Email: mentor@college.edu

Password: password123

You can now use your fully functional "Mentor's Eye" application!
