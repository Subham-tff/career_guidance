from flask import Flask, request, render_template
import sqlite3
import joblib
from pytrends.request import TrendReq

app = Flask(__name__)

# Load the trained model
model = joblib.load("career_model.pkl")

# Connect to SQLite database
conn = sqlite3.connect("career.db", check_same_thread=False)
cursor = conn.cursor()

# Create users table if it doesn't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT,
    answers TEXT,
    recommendation TEXT
)
""")
conn.commit()

# Psychological questions
questions = [
    {"question": "Do you enjoy solving complex problems?", "category": ["tech", "analytical"], "weight": 2},
    {"question": "Are you more creative than analytical?", "category": ["creative"], "weight": 1},
    {"question": "Do you prefer working in teams rather than alone?", "category": ["social"], "weight": 1},
    {"question": "Are you interested in technology and gadgets?", "category": ["tech"], "weight": 2},
    {"question": "Do you enjoy helping others and working in social settings?", "category": ["social"], "weight": 1},
    {"question": "Do you like working with numbers and data?", "category": ["analytical"], "weight": 2},
    {"question": "Are you passionate about art, music, or design?", "category": ["creative"], "weight": 2},
    {"question": "Do you enjoy teaching or mentoring others?", "category": ["social"], "weight": 1},
    {"question": "Are you curious about how machines and software work?", "category": ["tech"], "weight": 2},
    {"question": "Do you prefer logical reasoning over emotional decision-making?", "category": ["analytical"], "weight": 1},
]

# Home page
@app.route("/")
def home():
    return render_template("index.html")

# Test page
@app.route("/test", methods=["GET", "POST"])
def test():
    if request.method == "POST":
        # Get user answers
        answers = {f"q{i}": int(request.form.get(f"q{i}", 0)) for i in range(1, 11)}
        
        # Predict career
        recommendation = predict_career(answers)
        
        # Save user data to database
        name = request.form.get("name")
        email = request.form.get("email")
        save_user_data(name, email, answers, recommendation)
        
        # Fetch market trends
        trends = fetch_market_trends()
        
        return render_template("result.html", recommendation=recommendation, trends=trends)
    return render_template("test.html", questions=questions)

# Function to predict career
def predict_career(answers):
    input_data = [answers.get(f"q{i}", 0) for i in range(1, 11)]
    prediction = model.predict([input_data])
    return prediction[0]

# Function to save user data
def save_user_data(name, email, answers, recommendation):
    cursor.execute("""
    INSERT INTO users (name, email, answers, recommendation)
    VALUES (?, ?, ?, ?)
    """, (name, email, str(answers), recommendation))
    conn.commit()

# Function to fetch market trends
def fetch_market_trends():
    pytrends = TrendReq(hl='en-US', tz=360)
    pytrends.build_payload(kw_list=["data scientist", "software engineer", "graphic designer"])
    trends = pytrends.interest_over_time()
    return trends.to_string()

if __name__ == "__main__":
    app.run(debug=True)
