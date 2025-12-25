# AI-Based Smart School Administration System

## Module 1: Early Warning System for Student Risk Detection

An AI-powered system to identify at-risk students using machine learning with 98% accuracy.

---

## 🎯 Current Status

**Module 1:** ✅ Phase 1 Complete (Project Setup)
- Risk Detection Model: 98% Accuracy (Gradient Boosting)
- Frontend: Streamlit 1.52.2
- Backend: Flask REST API 3.1.2
- Architecture: Hybrid (Streamlit + Flask API)

---

## 📁 Project Structure

ai-school-admin-system/
├── frontend/ # Streamlit UI
│ ├── pages/ # Multi-page app pages
│ ├── utils/ # Helper functions
│ ├── assets/ # Images, CSS
│ └── app.py # Main Streamlit app
├── backend/ # Flask REST API
│ ├── routes/ # API endpoints
│ ├── services/ # Business logic
│ ├── utils/ # Utilities
│ ├── config/ # Configuration
│ └── api.py # Main Flask app
├── models/ # Trained ML models
│ └── saved_models/ # Pickled models
├── data/ # Datasets
│ ├── raw/ # Original data
│ ├── processed/ # Preprocessed data
│ └── synthetic/ # Generated data
├── docs/ # Documentation
├── tests/ # Test files
└── scripts/ # Utility scripts



---

## 🛠️ Tech Stack

### Frontend
- **Streamlit 1.52.2** - Web UI framework
- **Plotly 6.5.0** - Interactive visualizations
- **pandas 2.3.3** - Data manipulation
- **numpy 2.4.0** - Numerical computing

### Backend
- **Flask 3.1.2** - REST API framework
- **Flask-CORS 6.0.2** - Cross-origin support
- **Flask-RESTful 0.3.10** - REST utilities

### Machine Learning
- **scikit-learn 1.8.0** - ML algorithms
- **Gradient Boosting** - 98% accuracy model
- **SMOTE** - Class balancing
- **17 engineered features**

---

## 🚀 Installation

### Prerequisites
- Python 3.10+
- pip package manager

### Setup Steps

Clone repository (if using Git)
git clone <repository-url>
cd ai-school-admin-system

Create virtual environment
python -m venv venv

Activate virtual environment
Windows:
venv\Scripts\activate

Linux/Mac:
source venv/bin/activate

Install dependencies
pip install -r backend/requirements.txt
pip install -r frontend/requirements.txt

text

---

## 📊 Model Performance

| Metric | Value |
|--------|-------|
| **Accuracy** | 98.00% |
| **Precision** | 98.03% |
| **Recall** | 98.00% |
| **F1-Score** | 98.00% |
| **ROC-AUC** | 99.94% |
| **Test Samples** | 200 |
| **Correct Predictions** | 196/200 |

---

## 🎯 Features

### Current (Module 1)
- ✅ Student risk level prediction (Low, Medium, High, Critical)
- ✅ Confidence scores for each prediction
- ✅ Interactive web interface
- ✅ REST API for integrations
- ✅ Real-time predictions

### Planned (Modules 2-4)
- ⏳ Behavioral pattern analysis
- ⏳ Attendance prediction
- ⏳ Institutional performance dashboard

---

## 👨‍💻 Author

Developed as part of B.Tech Final Year Project
Institution: [Your College Name]
Year: 2024-2025

---

## 📅 Development Timeline

- **Phase 1:** ✅ Project Setup (Dec 25, 2025)
- **Phase 2:** 🔄 Backend Development (In Progress)
- **Phase 3:** ⏳ Frontend Development
- **Phase 4:** ⏳ Integration & Testing
- **Phase 5:** ⏳ Documentation & Polish

---

## 📝 License

Educational Project - All Rights Reserved