"""
Backend Configuration Settings
"""
import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent.parent
MODEL_DIR = BASE_DIR / "models" / "saved_models"
DATA_DIR = BASE_DIR / "data"

# API Configuration
API_HOST = os.getenv("API_HOST", "127.0.0.1")
API_PORT = int(os.getenv("API_PORT", 5000))
DEBUG = os.getenv("FLASK_DEBUG", "True") == "True"

# Model paths
MODEL_PATH = MODEL_DIR / "best_model.pkl"
SCALER_PATH = MODEL_DIR / "scaler.pkl"
ENCODERS_PATH = MODEL_DIR / "label_encoders.pkl"
METADATA_PATH = MODEL_DIR / "model_metadata.pkl"

# Risk level mappings
RISK_LABELS = {
    0: 'Low Risk',
    1: 'Medium Risk',
    2: 'High Risk',
    3: 'Critical Risk'
}

RISK_COLORS = {
    0: 'green',
    1: 'orange',
    2: 'red',
    3: 'darkred'
}

# Feature names (must match training data)
FEATURE_NAMES = [
    'age', 'gender_encoded', 'grade', 'socioeconomic_status_encoded',
    'parent_education_encoded', 'current_gpa', 'previous_gpa',
    'grade_trend', 'attendance_percentage', 'failed_subjects',
    'assignment_submission_rate', 'disciplinary_incidents',
    'counseling_visits', 'consecutive_absences', 'late_arrivals',
    'library_visits', 'extracurricular_participation'
]

# Valid input values
VALID_GENDERS = ['Male', 'Female']
VALID_SES = ['Low', 'Medium', 'High']
VALID_PARENT_EDU = ['None', 'High School', 'Graduate', 'Post-Graduate']
VALID_GRADES = [9, 10, 11, 12]

print(f"✓ Configuration loaded")
print(f"  Model directory: {MODEL_DIR}")
print(f"  API will run on: {API_HOST}:{API_PORT}")
