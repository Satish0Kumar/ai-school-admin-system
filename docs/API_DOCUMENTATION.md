# API Documentation - Module 1: Early Warning System

## Base URL
http://127.0.0.1:5000/api

## Authentication
Currently no authentication required (Development mode)

---

## Endpoints

### 1. Health Check
Endpoint: GET /api/health

Response:
{
  "success": true,
  "status": "healthy",
  "service": "AI School Admin API",
  "module": "Risk Detection",
  "version": "1.0.0"
}

---

### 2. Get Model Information
Endpoint: GET /api/risk/model-info

Response:
{
  "success": true,
  "model_info": {
    "model_name": "Gradient Boosting",
    "accuracy": "98.00%",
    "precision": "98.03%",
    "recall": "98.00%",
    "f1_score": "98.00%",
    "trained_date": "2025-12-25 08:11:35",
    "features_count": 17
  }
}

---

### 3. Predict Single Student Risk
Endpoint: POST /api/risk/predict

Request Body:
{
  "age": 16,
  "gender": "Male",
  "grade": 10,
  "socioeconomic_status": "Medium",
  "parent_education": "Graduate",
  "current_gpa": 70.0,
  "previous_gpa": 72.0,
  "attendance_percentage": 82.0,
  "failed_subjects": 1,
  "assignment_submission_rate": 80.0,
  "disciplinary_incidents": 1
}

Response:
{
  "success": true,
  "prediction": "Medium Risk",
  "risk_level": 1,
  "confidence": 97.85
}

---

### 4. Predict Batch Student Risks
Endpoint: POST /api/risk/predict-batch
