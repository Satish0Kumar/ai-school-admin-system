# ScholarSense - AI-Powered Academic Intelligence System

## 🎓 Overview
ScholarSense is a comprehensive school administration system with AI-powered student dropout risk prediction, designed to help educators identify and support at-risk students proactively.

## ✨ Features

### Core Functionality
- **Student Management** - Complete CRUD operations for student records
- **Academic Tracking** - Monitor GPA, grades, and academic performance
- **Risk Prediction** - ML-based dropout risk assessment
- **User Authentication** - Secure JWT-based authentication
- **Role-Based Access** - Admin and Teacher roles with different permissions
- **Interactive Dashboard** - Real-time metrics and visualizations

### Key Modules
1. **Module 1: Risk Prediction Engine** ✅ COMPLETE
   - AI/ML-based risk classification (Low, Medium, High, Critical)
   - Confidence scoring and probability distribution
   - Feature-based predictions using 17+ data points

2. **Student Management System** ✅ COMPLETE
   - Add, view, edit, and manage student records
   - Search and filter functionality
   - Detailed student profiles

3. **Academic Records System** ✅ COMPLETE
   - Track semester-wise performance
   - Subject-wise scoring
   - GPA trends and analysis

## 🏗️ Tech Stack

### Backend
- **Framework:** Flask (Python)
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy
- **Authentication:** JWT with Flask-JWT-Extended
- **Password Security:** bcrypt
- **API:** RESTful architecture

### Frontend
- **Framework:** Streamlit
- **Charts:** Plotly
- **HTTP Client:** Requests

### Machine Learning
- **Model:** Scikit-learn (Gradient Boosting/Random Forest)
- **Features:** 17 student attributes
- **Output:** 4-level risk classification

## 📊 System Architecture

┌─────────────────────────────────────────────────────────┐
│ Streamlit Frontend │
│ (Login, Dashboard, Students, Profile, Predictions) │
└───────────────────┬─────────────────────────────────────┘
│ HTTP/REST API
┌───────────────────▼─────────────────────────────────────┐
│ Flask Backend │
│ (Authentication, Business Logic, ML Integration) │
└───────────────────┬─────────────────────────────────────┘
│ SQLAlchemy ORM
┌───────────────────▼─────────────────────────────────────┐
│ PostgreSQL Database │
│ (Students, Academic Records, Predictions, Users) │
└─────────────────────────────────────────────────────────┘

text

## 🚀 Installation & Setup

### Prerequisites
- Python 3.10+
- PostgreSQL 14+
- pip (Python package manager)

### Step 1: Clone Repository
```bash
git clone <repository-url>
cd ai-school-admin-system
Step 2: Create Virtual Environment
bash
python -m venv venv
.\venv\Scripts\Activate  # Windows
source venv/bin/activate # Linux/Mac
Step 3: Install Dependencies
bash
pip install flask flask-cors flask-jwt-extended python-dotenv
pip install sqlalchemy psycopg2-binary bcrypt
pip install streamlit plotly pandas requests
Step 4: Setup Database
bash
# Create PostgreSQL database
psql -U postgres
CREATE DATABASE scholarsense;
CREATE USER scholar_admin WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE scholarsense TO scholar_admin;
\q

# Initialize schema
psql -U scholar_admin -d scholarsense -f backend/database/schema.sql
Step 5: Configure Environment
Create .env file:

text
# Database
DB_NAME=scholarsense
DB_USER=scholar_admin
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

# Security
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ACCESS_TOKEN_EXPIRES=3600

**⚠️ IMPORTANT:** SECRET_KEY and JWT_SECRET_KEY are now REQUIRED environment variables. The application will not start without them to prevent insecure deployments.

# Application
PROJECT_NAME=ScholarSense
FLASK_ENV=development
Step 6: Create Default Users
bash
python -m backend.auth.auth_service
Step 7: Start Backend API
bash
python backend/api.py
API will run on: http://localhost:5000

Step 8: Start Frontend (New Terminal)
bash
streamlit run frontend/app.py
UI will open at: http://localhost:8501

🔐 Default Credentials
Admin Account:

Email: admin@scholarsense.com

Password: admin123

Teacher Account:

Email: teacher@scholarsense.com

Password: teacher123

📁 Project Structure
text
ai-school-admin-system/
├── backend/
│   ├── api.py                      # Flask REST API
│   ├── database/
│   │   ├── schema.sql              # Database schema
│   │   ├── communications_migration.sql  # Database migrations
│   │   ├── db_config.py            # Database configuration
│   │   └── models.py               # SQLAlchemy models
│   ├── auth/
│   │   └── auth_service.py         # Authentication service
│   ├── scripts/
│   │   ├── fix_risk_prediction_scales.py  # Data repair script
│   │   ├── fix_deprecations.ps1    # Deprecation fixes
│   │   └── patch_plotly_dark.py    # Plotly theme patch
│   └── services/
│       ├── student_service.py      # Student CRUD
│       ├── academic_service.py     # Academic records
│       └── prediction_service.py   # ML predictions
├── frontend/
│   ├── app.py                      # Login page
│   ├── pages/
│   │   ├── 1_📊_Dashboard.py      # Main dashboard
│   │   ├── 2_👥_Students.py       # Student list
│   │   ├── 3_👤_Student_Profile.py # Student details
│   │   ├── 4_🎯_Predictions.py    # Risk predictions
│   │   ├── 5_📅_Attendance.py     # Attendance tracking
│   │   ├── 6_📝_Incident_Logging.py # Behavioral incidents
│   │   ├── 7_🔔_Notifications.py  # System notifications
│   │   ├── 8_🧠_Behavioral_Dashboard.py # Behavior analytics
│   │   ├── 9_📝_Marks_Entry.py    # Academic marks
│   │   ├── 10_🔁_Batch_Analysis.py # Batch predictions
│   │   ├── 11_📧_Parent_Portal.py # Parent communication
│   │   ├── 12_📈_Analytics.py     # System analytics
│   │   └── 13_👤_User_Management.py # User administration
│   └── utils/
│       ├── api_client.py           # API communication
│       └── session_manager.py      # Session handling
├── scripts/
│   ├── demo_presentation.py        # Demo scripts
│   ├── reset_passwords_deprecated.py # Legacy utilities
│   └── train_model.py              # ML training
├── tests/
│   ├── test_api.py                 # API tests
│   └── test_integration.py         # Integration tests
├── models/
│   └── saved_models/               # ML model files
├── data/
│   ├── processed/                  # Processed datasets
│   └── raw/                        # Raw data files
├── docs/                           # Documentation
├── .env                            # Environment variables (REQUIRED)
├── .gitignore                     # Git ignore rules
└── README.md                       # Documentation

## 🔄 Recent Changes

### v2.1.0 - Code Quality & Security Improvements
- **Security**: Removed hardcoded fallback secret keys - now requires explicit environment variables
- **Bug Fix**: Fixed key name mismatches in prediction service (`attendance_percentage` → `attendance_rate`, `disciplinary_incidents` → `behavioral_incidents`)
- **Cleanup**: Moved utility scripts to `scripts/` directory
- **Cleanup**: Moved database migrations to `backend/database/`
- **Cleanup**: Moved test files to `tests/` directory
- **Cleanup**: Removed committed log files and added `*.log` to `.gitignore`
- **Refactor**: Removed deprecated `age` field from Student model (now computed from `date_of_birth`)
- **UI**: Fixed page numbering gap (renamed User Management to page 13)

🎯 API Endpoints
Authentication
POST /api/auth/login - User login

GET /api/auth/verify - Verify token

GET /api/auth/me - Get current user

Students
GET /api/students - List all students

GET /api/students/{id} - Get student by ID

POST /api/students - Create student

PUT /api/students/{id} - Update student

DELETE /api/students/{id} - Delete student

Academic Records
GET /api/students/{id}/academics - Get student's records

POST /api/academics - Create academic record

PUT /api/academics/{id} - Update record

Predictions
POST /api/students/{id}/predict - Make prediction

GET /api/students/{id}/predictions - Get prediction history

GET /api/predictions/high-risk - Get high-risk students

📈 Usage
1. Login
Access http://localhost:8501 and login with credentials

2. View Dashboard
See overview of students, metrics, and risk distribution

3. Manage Students
Add, view, edit student records

4. Add Academic Records
Enter semester grades and performance data

5. Make Predictions
Generate risk predictions for students

6. Monitor High-Risk Students
View and track students needing intervention

🔧 Development
Run Tests
bash
python -m backend.services.student_service
python -m backend.services.academic_service
python -m backend.services.prediction_service
Database Queries
bash
psql -U scholar_admin -d scholarsense
📊 Current Status
✅ Completed:

Database design and implementation

JWT authentication system

REST API (30+ endpoints)

Student management

Academic records tracking

ML prediction engine (with dummy model)

Complete Streamlit UI

End-to-end workflow

🔄 In Progress:

Actual ML model integration

Attendance tracking module

Behavioral incident logging

🤝 Contributing
Contributions welcome! Please create issues and pull requests.

📝 License
Educational Project - 2026

👨‍💻 Developer
Built with ❤️ by [Your Name]
Final Year B.Tech Project

Note: This is an educational project demonstrating full-stack development with AI/ML integration.


