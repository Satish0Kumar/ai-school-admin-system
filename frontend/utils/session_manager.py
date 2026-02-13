"""
Session Management for Streamlit
ScholarSense - AI-Powered Academic Intelligence System
"""
import streamlit as st
from datetime import datetime, timedelta
from frontend.utils.api_client import APIClient

class SessionManager:
    """Manage user authentication state in Streamlit"""
    
    @staticmethod
    def initialize_session():
        """Initialize session state variables"""
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = False
        if 'user' not in st.session_state:
            st.session_state.user = None
        if 'token' not in st.session_state:
            st.session_state.token = None
        if 'token_expiry' not in st.session_state:
            st.session_state.token_expiry = None
    
    @staticmethod
    def login(email: str, password: str):
        """
        Login user and store session
        Returns: True if successful, error message otherwise
        """
        result = APIClient.login(email, password)
        
        if 'error' not in result:
            st.session_state.authenticated = True
            st.session_state.user = result['user']
            st.session_state.token = result['access_token']
            st.session_state.token_expiry = datetime.now() + timedelta(hours=1)
            return True
        else:
            return result['error']
    
    @staticmethod
    def logout():
        """Logout user and clear session"""
        st.session_state.authenticated = False
        st.session_state.user = None
        st.session_state.token = None
        st.session_state.token_expiry = None
    
    @staticmethod
    def is_authenticated():
        """Check if user is authenticated"""
        if not st.session_state.get('authenticated'):
            return False
        
        # Check token expiry
        if st.session_state.get('token_expiry'):
            if datetime.now() >= st.session_state.token_expiry:
                SessionManager.logout()
                return False
        
        return True
    
    @staticmethod
    def get_user():
        """Get current user info"""
        return st.session_state.get('user')
    
    @staticmethod
    def get_token():
        """Get JWT token"""
        return st.session_state.get('token')
    
    @staticmethod
    def is_admin():
        """Check if current user is admin"""
        user = SessionManager.get_user()
        return user and user.get('role') == 'admin'
    
    @staticmethod
    def require_auth():
        """Require authentication - redirect to login if not authenticated"""
        if not SessionManager.is_authenticated():
            st.warning("⚠️ Please login to access this page")
            st.switch_page("app.py")
            st.stop()
