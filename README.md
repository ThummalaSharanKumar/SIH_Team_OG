# SIH_Team_OG
This project builds an AI-driven system to predict student dropout risk using data like attendance, grades, engagement, and fee status. With feature engineering, a Random Forest model, and visual insights, it highlights at-risk students early, enabling educators to take proactive, data-driven interventions.


Here is a complete guide on how to set up and run your "Mentor's Eye" application on your system or any new system, assuming all the project files are in one folder.

To make this process easier, I've also created a requirements.txt file for you. This file lists all the necessary Python libraries, allowing you to install them with a single command.

Code snippet

flask
pandas
scikit-learn
joblib
Faker
numpy
seaborn
matplotlib
eof

---
### ## Setup and Execution Guide

Follow these steps in order. The setup (Steps 1-3) only needs to be done once on a new system.

#### **Step 1: Set Up a Virtual Environment (Recommended)**
It's a best practice to create an isolated environment for your project. Open your terminal or command prompt in your project folder and run:

bash
# Create the virtual environment
python -m venv .venv

# Activate it (on Windows)
.venv\Scripts\activate

# Activate it (on Mac/Linux)
source .venv/bin/activate
Step 2: Install All Required Libraries
With your virtual environment active, use the provided requirements.txt file to install all the project's dependencies in one go.

Bash

pip install -r requirements.txt
Step 3: Run the One-Time Setup Scripts
You must run the following four scripts in this specific order. They will create your database, train your model, generate the historical data, and move that data into the database.

python database_setup.py

python train_model.py

python generate_historical_data.py

python migrate_data.py

Step 4: Run the Application
After the one-time setup is complete, you can now start your web application.

Bash

python app.py
Step 5: Access the Dashboard
Open your web browser and go to the following address. You will be greeted by the login page.

http://127.0.0.1:5000

Use the credentials mentor@college.edu and password123 to log in and use your fully functional dashboard.
