"""
Model Service - Handles ML model loading and predictions
"""
import pickle
import pandas as pd
from pathlib import Path
import sys

# Add backend to path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from config.settings import (
    MODEL_PATH, SCALER_PATH, ENCODERS_PATH, METADATA_PATH,
    RISK_LABELS, FEATURE_NAMES
)


class ModelService:
    """Service for loading and using ML models"""
    
    def __init__(self):
        self.model = None
        self.scaler = None
        self.encoders = None
        self.metadata = None
        self.load_models()
    
    def load_models(self):
        """Load all trained models and preprocessors"""
        try:
            print("\n" + "="*60)
            print("LOADING ML MODELS")
            print("="*60)
            
            # Load main model
            with open(MODEL_PATH, 'rb') as f:
                self.model = pickle.load(f)
            print(f"✓ Loaded prediction model: {MODEL_PATH.name}")
            
            # Load scaler
            with open(SCALER_PATH, 'rb') as f:
                self.scaler = pickle.load(f)
            print(f"✓ Loaded feature scaler: {SCALER_PATH.name}")
            
            # Load encoders
            with open(ENCODERS_PATH, 'rb') as f:
                self.encoders = pickle.load(f)
            print(f"✓ Loaded label encoders: {ENCODERS_PATH.name}")
            
            # Load metadata
            with open(METADATA_PATH, 'rb') as f:
                self.metadata = pickle.load(f)
            print(f"✓ Loaded model metadata: {METADATA_PATH.name}")
            
            print("\n" + "="*60)
            print(f"MODEL INFO")
            print("="*60)
            print(f"  Model Type: {self.metadata.get('model_name', 'Unknown')}")
            print(f"  Accuracy: {self.metadata.get('test_accuracy', 0)*100:.2f}%")
            print(f"  Trained: {self.metadata.get('trained_date', 'Unknown')}")
            print("="*60 + "\n")
            
            return True
            
        except Exception as e:
            print(f"❌ Error loading models: {str(e)}")
            raise
    
    def encode_features(self, student_data):
        """Encode categorical features"""
        try:
            # Encode gender
            gender_enc = self.encoders['gender'].transform([student_data['gender']])[0]
            
            # Encode socioeconomic status
            ses_enc = self.encoders['socioeconomic_status'].transform(
                [student_data['socioeconomic_status']]
            )[0]
            
            # Encode parent education
            parent_enc = self.encoders['parent_education'].transform(
                [student_data['parent_education']]
            )[0]
            
            return gender_enc, ses_enc, parent_enc
            
        except Exception as e:
            raise ValueError(f"Error encoding features: {str(e)}")
    
    def prepare_features(self, student_data):
        """Prepare features for prediction"""
        try:
            # Encode categorical features
            gender_enc, ses_enc, parent_enc = self.encode_features(student_data)
            
            # Calculate grade trend
            grade_trend = student_data['current_gpa'] - student_data['previous_gpa']
            
            # Create feature dictionary in correct order
            features_dict = {
                'age': student_data['age'],
                'gender_encoded': gender_enc,
                'grade': student_data['grade'],
                'socioeconomic_status_encoded': ses_enc,
                'parent_education_encoded': parent_enc,
                'current_gpa': student_data['current_gpa'],
                'previous_gpa': student_data['previous_gpa'],
                'grade_trend': grade_trend,
                'attendance_percentage': student_data['attendance_percentage'],
                'failed_subjects': student_data['failed_subjects'],
                'assignment_submission_rate': student_data['assignment_submission_rate'],
                'disciplinary_incidents': student_data['disciplinary_incidents'],
                'counseling_visits': student_data.get('counseling_visits', 0),
                'consecutive_absences': student_data.get('consecutive_absences', 0),
                'late_arrivals': student_data.get('late_arrivals', 0),
                'library_visits': student_data.get('library_visits', 0),
                'extracurricular_participation': student_data.get('extracurricular_participation', 0)
            }
            
            # Create DataFrame
            features_df = pd.DataFrame([features_dict])
            
            return features_df
            
        except Exception as e:
            raise ValueError(f"Error preparing features: {str(e)}")
    
    def predict_risk(self, student_data):
        """Make risk prediction for a student"""
        try:
            # Prepare features
            features_df = self.prepare_features(student_data)
            
            # Scale features
            features_scaled = self.scaler.transform(features_df)
            
            # Make prediction
            prediction = self.model.predict(features_scaled)[0]
            probabilities = self.model.predict_proba(features_scaled)[0]
            
            # Prepare result
            result = {
                'success': True,
                'prediction': RISK_LABELS[prediction],
                'risk_level': int(prediction),
                'confidence': float(probabilities[prediction] * 100),
                'probabilities': {
                    'Low Risk': float(probabilities[0] * 100),
                    'Medium Risk': float(probabilities[1] * 100),
                    'High Risk': float(probabilities[2] * 100),
                    'Critical Risk': float(probabilities[3] * 100)
                },
                'recommendations': self.get_recommendations(prediction)
            }
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_recommendations(self, risk_level):
        """Get intervention recommendations based on risk level"""
        recommendations = {
            0: [
                "Student is performing well",
                "Continue current support strategies",
                "Consider as peer mentor for at-risk students"
            ],
            1: [
                "Monitor attendance and grade trends",
                "Encourage participation in study groups",
                "Regular check-ins with teacher"
            ],
            2: [
                "Schedule parent-teacher meeting",
                "Assign academic mentor or tutor",
                "Weekly progress monitoring required",
                "Consider counseling support"
            ],
            3: [
                "IMMEDIATE intervention required",
                "Emergency parent-teacher conference",
                "Assign dedicated counselor",
                "Daily attendance monitoring",
                "Enroll in intensive support program",
                "Consider alternative learning strategies"
            ]
        }
        return recommendations.get(risk_level, [])
    
    def get_model_info(self):
        """Get model metadata"""
        if self.metadata:
            return {
                'model_name': self.metadata.get('model_name', 'Unknown'),
                'accuracy': f"{self.metadata.get('test_accuracy', 0)*100:.2f}%",
                'precision': f"{self.metadata.get('precision', 0)*100:.2f}%",
                'recall': f"{self.metadata.get('recall', 0)*100:.2f}%",
                'f1_score': f"{self.metadata.get('f1_score', 0)*100:.2f}%",
                'trained_date': self.metadata.get('trained_date', 'Unknown'),
                'features_count': len(FEATURE_NAMES)
            }
        return {}


# Test the service
if __name__ == "__main__":
    print("Testing Model Service...")
    service = ModelService()
    print("\n✓ Model Service initialized successfully!")
    print(f"✓ Model Info: {service.get_model_info()}")
