"""
API Client for ScholarSense Backend
Handles all API communication
"""
import requests
import streamlit as st
from typing import Dict, List, Optional

class APIClient:
    """Client for communicating with ScholarSense API"""
    
    BASE_URL = "http://localhost:5000/api"
    
    @staticmethod
    def get_headers(token: str = None) -> Dict:
        """Get authorization headers"""
        if token is None:
            token = st.session_state.get('token')
        
        if token:
            return {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
        return {'Content-Type': 'application/json'}
    
    # ============================================
    # AUTHENTICATION
    # ============================================
    
    @staticmethod
    def login(email: str, password: str) -> Dict:
        """Login user"""
        try:
            response = requests.post(
                f"{APIClient.BASE_URL}/auth/login",
                json={'email': email, 'password': password},
                timeout=5
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {'error': response.json().get('error', 'Login failed')}
        except Exception as e:
            return {'error': f'Connection error: {str(e)}'}
    
    @staticmethod
    def verify_token(token: str) -> Dict:
        """Verify JWT token"""
        try:
            response = requests.get(
                f"{APIClient.BASE_URL}/auth/verify",
                headers=APIClient.get_headers(token),
                timeout=5
            )
            
            if response.status_code == 200:
                return response.json()
            return {'error': 'Invalid token'}
        except Exception as e:
            return {'error': str(e)}
    
    @staticmethod
    def get_current_user() -> Dict:
        """Get current user info"""
        try:
            response = requests.get(
                f"{APIClient.BASE_URL}/auth/me",
                headers=APIClient.get_headers(),
                timeout=5
            )
            
            if response.status_code == 200:
                return response.json()
            return {'error': 'Failed to get user'}
        except Exception as e:
            return {'error': str(e)}
    
    # ============================================
    # STUDENTS
    # ============================================
    
    @staticmethod
    def get_students(grade: int = None, section: str = None, search: str = None) -> List[Dict]:
        """Get all students with optional filters"""
        try:
            params = {}
            if grade:
                params['grade'] = grade
            if section:
                params['section'] = section
            if search:
                params['search'] = search
            
            response = requests.get(
                f"{APIClient.BASE_URL}/students",
                headers=APIClient.get_headers(),
                params=params,
                timeout=5
            )
            
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            st.error(f"Error fetching students: {e}")
            return []
    
    @staticmethod
    def get_student(student_id: int) -> Dict:
        """Get specific student"""
        try:
            response = requests.get(
                f"{APIClient.BASE_URL}/students/{student_id}",
                headers=APIClient.get_headers(),
                timeout=5
            )
            
            if response.status_code == 200:
                return response.json()
            return {'error': 'Student not found'}
        except Exception as e:
            return {'error': str(e)}
    
    @staticmethod
    def get_student_details(student_id: int) -> Dict:
        """Get student with all records"""
        try:
            response = requests.get(
                f"{APIClient.BASE_URL}/students/{student_id}/details",
                headers=APIClient.get_headers(),
                timeout=5
            )
            
            if response.status_code == 200:
                return response.json()
            return {'error': 'Student not found'}
        except Exception as e:
            return {'error': str(e)}
    
    @staticmethod
    def create_student(data: Dict) -> Dict:
        """Create new student"""
        try:
            response = requests.post(
                f"{APIClient.BASE_URL}/students",
                headers=APIClient.get_headers(),
                json=data,
                timeout=5
            )
            
            if response.status_code == 201:
                return response.json()
            return {'error': response.json().get('error', 'Failed to create student')}
        except Exception as e:
            return {'error': str(e)}
    
    @staticmethod
    def get_students_count() -> int:
        """Get total student count"""
        try:
            response = requests.get(
                f"{APIClient.BASE_URL}/students/count",
                headers=APIClient.get_headers(),
                timeout=5
            )
            
            if response.status_code == 200:
                return response.json().get('count', 0)
            return 0
        except Exception as e:
            return 0
    
    # ============================================
    # ACADEMIC RECORDS
    # ============================================
    
    @staticmethod
    def get_student_academics(student_id: int) -> List[Dict]:
        """Get student's academic records"""
        try:
            response = requests.get(
                f"{APIClient.BASE_URL}/students/{student_id}/academics",
                headers=APIClient.get_headers(),
                timeout=5
            )
            
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            return []
    
    @staticmethod
    def create_academic_record(data: Dict) -> Dict:
        """Create academic record"""
        try:
            response = requests.post(
                f"{APIClient.BASE_URL}/academics",
                headers=APIClient.get_headers(),
                json=data,
                timeout=5
            )
            
            if response.status_code == 201:
                return response.json()
            return {'error': response.json().get('error', 'Failed to create record')}
        except Exception as e:
            return {'error': str(e)}
    
    # ============================================
    # PREDICTIONS
    # ============================================
    
    @staticmethod
    def make_prediction(student_id: int) -> Dict:
        """Make risk prediction for student"""
        try:
            response = requests.post(
                f"{APIClient.BASE_URL}/students/{student_id}/predict",
                headers=APIClient.get_headers(),
                timeout=10
            )
            
            if response.status_code == 201:
                return response.json()
            return {'error': response.json().get('error', 'Prediction failed')}
        except Exception as e:
            return {'error': str(e)}
    
    @staticmethod
    def get_student_predictions(student_id: int, limit: int = 10) -> List[Dict]:
        """Get prediction history"""
        try:
            response = requests.get(
                f"{APIClient.BASE_URL}/students/{student_id}/predictions",
                headers=APIClient.get_headers(),
                params={'limit': limit},
                timeout=5
            )
            
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            return []
    
    @staticmethod
    def get_high_risk_students(grade: int = None) -> List[Dict]:
        """Get high-risk students"""
        try:
            params = {'grade': grade} if grade else {}
            response = requests.get(
                f"{APIClient.BASE_URL}/predictions/high-risk",
                headers=APIClient.get_headers(),
                params=params,
                timeout=5
            )
            
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            return []
    



    # ============================================
    # ATTENDANCE
    # ============================================
    
    @staticmethod
    def mark_attendance(student_id: int, date: str, status: str, remarks: str = None) -> Dict:
        """Mark attendance for a student"""
        try:
            response = requests.post(
                f"{APIClient.BASE_URL}/attendance/mark",
                headers=APIClient.get_headers(),
                json={
                    'student_id': student_id,
                    'date': date,
                    'status': status,
                    'remarks': remarks
                },
                timeout=5
            )
            
            if response.status_code in [200, 201]:
                return response.json()
            return {'error': response.json().get('error', 'Failed to mark attendance')}
        except Exception as e:
            return {'error': str(e)}
    
    @staticmethod
    def mark_bulk_attendance(attendance_list: List[Dict]) -> Dict:
        """Mark attendance for multiple students"""
        try:
            response = requests.post(
                f"{APIClient.BASE_URL}/attendance/bulk",
                headers=APIClient.get_headers(),
                json={'attendance_list': attendance_list},
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                return response.json()
            return {'error': response.json().get('error', 'Failed to mark bulk attendance')}
        except Exception as e:
            return {'error': str(e)}
    
    @staticmethod
    def get_student_attendance(student_id: int, start_date: str = None, end_date: str = None) -> List[Dict]:
        """Get attendance records for a student"""
        try:
            params = {}
            if start_date:
                params['start_date'] = start_date
            if end_date:
                params['end_date'] = end_date
            
            response = requests.get(
                f"{APIClient.BASE_URL}/students/{student_id}/attendance",
                headers=APIClient.get_headers(),
                params=params,
                timeout=5
            )
            
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            st.error(f"Error fetching attendance: {e}")
            return []
    
    @staticmethod
    def get_attendance_stats(student_id: int, days: int = 30) -> Dict:
        """Get attendance statistics"""
        try:
            response = requests.get(
                f"{APIClient.BASE_URL}/students/{student_id}/attendance/stats",
                headers=APIClient.get_headers(),
                params={'days': days},
                timeout=5
            )
            
            if response.status_code == 200:
                return response.json()
            return {'error': 'Failed to get stats'}
        except Exception as e:
            return {'error': str(e)}
    
    @staticmethod
    def get_daily_attendance(date: str, grade: int = None, section: str = None) -> List[Dict]:
        """Get daily attendance for all students"""
        try:
            params = {'date': date}
            
            # Only add params if they're not None
            if grade is not None:
                params['grade'] = str(grade)
            if section is not None:
                params['section'] = section
            
            print(f"🔍 Frontend API Client calling with params: {params}")  # Debug
            
            response = requests.get(
                f"{APIClient.BASE_URL}/attendance/daily",
                headers=APIClient.get_headers(),
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Frontend API Client received {len(data)} students")  # Debug
                return data
            else:
                print(f"❌ Frontend API Client error: {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ Frontend API Client exception: {e}")
            return []

    
    @staticmethod
    def get_low_attendance_students(threshold: float = 75.0, days: int = 30) -> List[Dict]:
        """Get students with low attendance"""
        try:
            response = requests.get(
                f"{APIClient.BASE_URL}/attendance/low-attendance",
                headers=APIClient.get_headers(),
                params={'threshold': threshold, 'days': days},
                timeout=5
            )
            
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            return []




    # ============================================
    # SYSTEM
    # ============================================
    
    @staticmethod
    def health_check() -> Dict:
        """Check API health"""
        try:
            response = requests.get(
                f"{APIClient.BASE_URL}/health",
                timeout=5
            )
            
            if response.status_code == 200:
                return response.json()
            return {'status': 'unhealthy'}
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
