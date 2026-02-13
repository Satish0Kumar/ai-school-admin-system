"""
Risk Prediction Service - ML Model Integration
ScholarSense - AI-Powered Academic Intelligence System
"""
import os
import pickle
import numpy as np
from datetime import datetime
from backend.database.models import Student, AcademicRecord, RiskPrediction, Attendance, BehavioralIncident
from backend.database.db_config import get_db
from sqlalchemy import func, desc

class PredictionService:
    """Handle ML-based risk predictions"""
    
    # Load ML model (your existing model from December)
    MODEL_PATH = 'models/saved_models/risk_model.pkl'
    model = None
    
    @classmethod
    def load_model(cls):
        """Load the trained ML model"""
        try:
            if os.path.exists(cls.MODEL_PATH):
                with open(cls.MODEL_PATH, 'rb') as f:
                    cls.model = pickle.load(f)
                print(f"✅ ML Model loaded from {cls.MODEL_PATH}")
                return True
            else:
                print(f"⚠️  ML Model not found at {cls.MODEL_PATH}")
                print(f"   Using dummy predictions for now")
                return False
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            return False
    
    @staticmethod
    def prepare_features(student_id: int):
        """
        Prepare features for ML model from database
        Returns: dict with all required features
        """
        db = next(get_db())
        try:
            # Get student
            student = db.query(Student).filter(Student.id == student_id).first()
            if not student:
                return {'error': 'Student not found'}
            
            # Get latest academic record
            academic = db.query(AcademicRecord).filter(
                AcademicRecord.student_id == student_id
            ).order_by(desc(AcademicRecord.recorded_date)).first()
            
            if not academic:
                return {'error': 'No academic records found for this student'}
            
            # Get attendance stats (last 30 days)
            from datetime import date, timedelta
            thirty_days_ago = date.today() - timedelta(days=30)
            
            total_days = db.query(func.count(Attendance.id)).filter(
                Attendance.student_id == student_id,
                Attendance.attendance_date >= thirty_days_ago
            ).scalar() or 0
            
            present_days = db.query(func.count(Attendance.id)).filter(
                Attendance.student_id == student_id,
                Attendance.attendance_date >= thirty_days_ago,
                Attendance.status == 'present'
            ).scalar() or 0
            
            attendance_rate = (present_days / total_days * 100) if total_days > 0 else 95.0
            
            # Get behavioral incidents (last 90 days)
            ninety_days_ago = date.today() - timedelta(days=90)
            incident_count = db.query(func.count(BehavioralIncident.id)).filter(
                BehavioralIncident.student_id == student_id,
                BehavioralIncident.incident_date >= ninety_days_ago
            ).scalar() or 0
            
            # Prepare features (matching your ML model's expected features)
            features = {
                'student_id': student.student_id,
                'age': student.age or 15,
                'grade': student.grade,
                'gender': 1 if student.gender == 'Male' else 0,
                'socioeconomic_status': {'Low': 0, 'Medium': 1, 'High': 2}.get(student.socioeconomic_status, 1),
                'parent_education': {'None': 0, 'High School': 1, 'Graduate': 2, 'Post-Graduate': 3}.get(student.parent_education, 1),
                'current_gpa': float(academic.current_gpa) if academic.current_gpa else 75.0,
                'previous_gpa': float(academic.previous_gpa) if academic.previous_gpa else 75.0,
                'grade_trend': float(academic.grade_trend) if academic.grade_trend else 0.0,
                'attendance_rate': attendance_rate,
                'failed_subjects': academic.failed_subjects or 0,
                'assignment_submission_rate': float(academic.assignment_submission_rate) if academic.assignment_submission_rate else 90.0,
                'behavioral_incidents': incident_count,
                'math_score': float(academic.math_score) if academic.math_score else 75.0,
                'science_score': float(academic.science_score) if academic.science_score else 75.0,
                'english_score': float(academic.english_score) if academic.english_score else 75.0,
                'social_score': float(academic.social_score) if academic.social_score else 75.0,
                'language_score': float(academic.language_score) if academic.language_score else 75.0
            }
            
            return features
        finally:
            db.close()
    
    @staticmethod
    def make_prediction(student_id: int, predicted_by: int = None):
        """
        Make risk prediction for a student
        Args:
            student_id: Database ID of student
            predicted_by: User ID who requested prediction
        Returns: Prediction result with probabilities
        """
        db = next(get_db())
        try:
            # Prepare features
            features = PredictionService.prepare_features(student_id)
            
            if 'error' in features:
                return features
            
            # Prepare feature array for model (17 features)
            feature_array = np.array([[
                features['age'],
                features['grade'],
                features['gender'],
                features['socioeconomic_status'],
                features['parent_education'],
                features['current_gpa'],
                features['previous_gpa'],
                features['grade_trend'],
                features['attendance_rate'],
                features['failed_subjects'],
                features['assignment_submission_rate'],
                features['behavioral_incidents'],
                features['math_score'],
                features['science_score'],
                features['english_score'],
                features['social_score'],
                features['language_score']
            ]])
            
            # Make prediction
            if PredictionService.model is not None:
                # Use actual model
                risk_level = PredictionService.model.predict(feature_array)[0]
                probabilities = PredictionService.model.predict_proba(feature_array)[0]
            else:
                # Dummy prediction based on GPA (for testing without model)
                gpa = features['current_gpa']
                if gpa >= 80:
                    risk_level = 0  # Low
                    probabilities = [0.70, 0.20, 0.08, 0.02]
                elif gpa >= 60:
                    risk_level = 1  # Medium
                    probabilities = [0.20, 0.60, 0.15, 0.05]
                elif gpa >= 40:
                    risk_level = 2  # High
                    probabilities = [0.05, 0.20, 0.60, 0.15]
                else:
                    risk_level = 3  # Critical
                    probabilities = [0.02, 0.08, 0.20, 0.70]
            
            # Map risk level to label
            risk_labels = {0: 'Low', 1: 'Medium', 2: 'High', 3: 'Critical'}
            risk_label = risk_labels[risk_level]
            
            # Get confidence score (probability of predicted class)
            confidence_score = probabilities[risk_level] * 100
            
            # Save prediction to database
            prediction = RiskPrediction(
                student_id=student_id,
                prediction_date=datetime.utcnow(),
                risk_level=int(risk_level),
                risk_label=risk_label,
                confidence_score=confidence_score,
                probability_low=probabilities[0] * 100,
                probability_medium=probabilities[1] * 100,
                probability_high=probabilities[2] * 100,
                probability_critical=probabilities[3] * 100,
                features_used=features,
                model_version='1.0',
                predicted_by=predicted_by
            )
            
            db.add(prediction)
            db.commit()
            db.refresh(prediction)
            
            return prediction.to_dict()
        except Exception as e:
            db.rollback()
            print(f"❌ Prediction error: {e}")
            return {'error': str(e)}
        finally:
            db.close()
    
    @staticmethod
    def get_student_predictions(student_id: int, limit: int = 10):
        """Get prediction history for a student"""
        db = next(get_db())
        try:
            predictions = db.query(RiskPrediction).filter(
                RiskPrediction.student_id == student_id
            ).order_by(desc(RiskPrediction.prediction_date)).limit(limit).all()
            
            return [pred.to_dict() for pred in predictions]
        finally:
            db.close()
    
    @staticmethod
    def get_latest_prediction(student_id: int):
        """Get latest prediction for a student"""
        db = next(get_db())
        try:
            prediction = db.query(RiskPrediction).filter(
                RiskPrediction.student_id == student_id
            ).order_by(desc(RiskPrediction.prediction_date)).first()
            
            if prediction:
                return prediction.to_dict()
            return {'error': 'No predictions found'}
        finally:
            db.close()
    
    @staticmethod
    def get_high_risk_students(grade: int = None):
        """Get list of high-risk students"""
        db = next(get_db())
        try:
            # Subquery to get latest prediction for each student
            subquery = db.query(
                RiskPrediction.student_id,
                func.max(RiskPrediction.prediction_date).label('max_date')
            ).group_by(RiskPrediction.student_id).subquery()
            
            query = db.query(Student, RiskPrediction).join(
                RiskPrediction, Student.id == RiskPrediction.student_id
            ).join(
                subquery,
                (RiskPrediction.student_id == subquery.c.student_id) &
                (RiskPrediction.prediction_date == subquery.c.max_date)
            ).filter(
                Student.is_active == True,
                RiskPrediction.risk_level >= 2  # High or Critical
            )
            
            if grade:
                query = query.filter(Student.grade == grade)
            
            results = query.all()
            
            return [{
                'student': student.to_dict(),
                'prediction': prediction.to_dict()
            } for student, prediction in results]
        finally:
            db.close()

# Initialize model on import
PredictionService.load_model()

# Test function
if __name__ == "__main__":
    print("=" * 60)
    print("🧪 TESTING PREDICTION SERVICE")
    print("=" * 60)
    
    # Get first student with academic records
    from backend.services.student_service import StudentService
    students = StudentService.get_all_students()
    
    if students:
        student_id = students[0]['id']
        print(f"\n🎯 Testing predictions for student ID: {student_id}")
        
        # Test 1: Prepare features
        print("\n1. Preparing features...")
        features = PredictionService.prepare_features(student_id)
        if 'error' not in features:
            print(f"   ✅ Features prepared: {len(features)} features")
            print(f"      GPA: {features['current_gpa']}, Attendance: {features['attendance_rate']:.1f}%")
        else:
            print(f"   ❌ {features['error']}")
        
        # Test 2: Make prediction
        print("\n2. Making prediction...")
        prediction = PredictionService.make_prediction(student_id)
        if 'error' not in prediction:
            print(f"   ✅ Prediction made!")
            print(f"      Risk Level: {prediction['risk_label']}")
            print(f"      Confidence: {prediction['confidence_score']:.1f}%")
        else:
            print(f"   ❌ {prediction['error']}")
        
        # Test 3: Get prediction history
        print("\n3. Getting prediction history...")
        history = PredictionService.get_student_predictions(student_id)
        print(f"   ✅ Found {len(history)} predictions")
        
    else:
        print("\n❌ No students found. Create a student and academic record first!")
    
    print("\n" + "=" * 60)
