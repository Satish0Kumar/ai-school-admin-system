"""
API Client - Handles communication with Flask backend
"""
import requests
import streamlit as st
import os

# Get API base URL from environment or use default
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:5000/api")


class APIClient:
    """Client for interacting with the Flask API"""
    
    def __init__(self, base_url=API_BASE_URL):
        self.base_url = base_url
        self.timeout = 10
    
    def health_check(self):
        """Check if API is healthy"""
        try:
            response = requests.get(
                f"{self.base_url.replace('/api', '')}/api/health",
                timeout=self.timeout
            )
            if response.status_code == 200:
                return True, response.json()
            return False, None
        except Exception as e:
            return False, str(e)
    
    def get_model_info(self):
        """Get model information"""
        try:
            response = requests.get(
                f"{self.base_url}/risk/model-info",
                timeout=self.timeout
            )
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    return data.get('model_info', {})
            return None
        except Exception as e:
            st.error(f"Error fetching model info: {str(e)}")
            return None
    
    def predict_risk(self, student_data):
        """Predict risk for a single student"""
        try:
            response = requests.post(
                f"{self.base_url}/risk/predict",
                json=student_data,
                headers={'Content-Type': 'application/json'},
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 400:
                error_data = response.json()
                st.error(f"Validation Error: {error_data.get('error', 'Invalid input')}")
                return None
            else:
                st.error(f"API Error: Status {response.status_code}")
                return None
                
        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to API. Make sure the Flask server is running!")
            st.info("Start the API with: `python backend/api.py`")
            return None
        except Exception as e:
            st.error(f"Error making prediction: {str(e)}")
            return None
    
    def predict_batch(self, students_list):
        """Predict risk for multiple students"""
        try:
            response = requests.post(
                f"{self.base_url}/risk/predict-batch",
                json={"students": students_list},
                headers={'Content-Type': 'application/json'},
                timeout=self.timeout * 2  # Longer timeout for batch
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"API Error: Status {response.status_code}")
                return None
                
        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to API. Make sure the Flask server is running!")
            return None
        except Exception as e:
            st.error(f"Error making batch prediction: {str(e)}")
            return None


# Create singleton instance
api_client = APIClient()
