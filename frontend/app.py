"""
ScholarSense - Main Application
AI-Powered Academic Intelligence System
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import streamlit as st
from frontend.utils.session_manager import SessionManager
from frontend.utils.api_client import APIClient

# Page configuration
st.set_page_config(
    page_title="ScholarSense - Login",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Initialize session
SessionManager.initialize_session()

# Professional CSS with HIGH CONTRAST
st.markdown("""
<style>
    /* Clean white background */
    .main {
        background-color: #f7fafc;
    }
    .stApp {
        background-color: #f7fafc;
    }
    
    /* Login container - white with shadow */
    .login-box {
        background: white;
        padding: 3rem;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        max-width: 450px;
        margin: 2rem auto;
        border: 1px solid #e2e8f0;
    }
    
    /* Logo and title */
    .logo {
        text-align: center;
        font-size: 4rem;
        margin-bottom: 1rem;
    }
    .app-title {
        text-align: center;
        color: #1a202c;
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        letter-spacing: -0.5px;
    }
    .app-subtitle {
        text-align: center;
        color: #4a5568;
        font-size: 1.1rem;
        margin-bottom: 2rem;
        font-weight: 500;
    }
    
    /* Section headers */
    .section-header {
        color: #1a202c;
        font-size: 1.3rem;
        font-weight: 700;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Input fields */
    .stTextInput > label {
        color: #2d3748 !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    .stTextInput > div > div > input {
        border: 2px solid #cbd5e0 !important;
        border-radius: 10px !important;
        padding: 0.75rem 1rem !important;
        font-size: 1rem !important;
        color: #1a202c !important;
        background-color: white !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #2563eb !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1) !important;
    }
    
    /* Primary button - blue with white text */
    .stButton > button[kind="primary"] {
        width: 100%;
        background: #2563eb !important;
        color: white !important;
        border: none !important;
        padding: 0.875rem 1.5rem !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        margin-top: 0.5rem !important;
        transition: all 0.2s !important;
        letter-spacing: 0.5px !important;
    }
    
    .stButton > button[kind="primary"]:hover {
        background: #1d4ed8 !important;
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(37, 99, 235, 0.3) !important;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        color: #4a5568;
        font-size: 0.9rem;
        margin-top: 3rem;
        padding: 1rem;
    }
    
    .footer-school {
        font-weight: 600;
        color: #2d3748;
    }
    
    /* Demo credentials box */
    .stExpander {
        background: #edf2f7;
        border: 1px solid #cbd5e0;
        border-radius: 10px;
        margin-top: 2rem;
    }
    
    .stExpander summary {
        color: #2d3748 !important;
        font-weight: 600 !important;
    }
    
    /* Alert messages */
    .stAlert {
        border-radius: 10px;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Check if already authenticated
if SessionManager.is_authenticated():
    st.switch_page("pages/1_📊_Dashboard.py")

# Check API health
with st.spinner("Checking system status..."):
    health = APIClient.health_check()
    if health.get('status') != 'healthy':
        st.error("⚠️ **Cannot connect to backend server**")
        st.info("Please ensure the Flask API is running:")
        st.code("python backend/api.py", language="bash")
        st.stop()

# Login Page Header
st.markdown('<div class="logo">🎓</div>', unsafe_allow_html=True)
st.markdown('<h1 class="app-title">ScholarSense</h1>', unsafe_allow_html=True)
st.markdown('<p class="app-subtitle">AI-Powered Academic Intelligence System</p>', unsafe_allow_html=True)

# Login Form
st.markdown('<div class="section-header">🔐 Login to Continue</div>', unsafe_allow_html=True)

email = st.text_input(
    "📧 Email Address",
    placeholder="admin@scholarsense.com",
    key="login_email"
)

password = st.text_input(
    "🔒 Password",
    type="password",
    placeholder="Enter your password",
    key="login_password"
)

# Login button
col1, col2 = st.columns([3, 1])
with col1:
    login_button = st.button("LOGIN", type="primary", use_container_width=True)

# Handle login
if login_button:
    if not email or not password:
        st.error("❌ Please enter both email and password")
    else:
        with st.spinner("Authenticating..."):
            result = SessionManager.login(email, password)
            
            if result == True:
                st.success("✅ Login successful! Redirecting...")
                st.rerun()
            else:
                st.error(f"❌ {result}")

# Footer
st.markdown("---")
st.markdown("""
<div class="footer">
    <p class="footer-school">🏫 Greenwood High School • Academic Year 2025-26</p>
    <p style="margin-top: 0.5rem;">Powered by AI • Built for Excellence</p>
</div>
""", unsafe_allow_html=True)

# Demo credentials
with st.expander("🔑 Demo Credentials"):
    st.markdown("""
    **Admin Account:**
    - Email: `admin@scholarsense.com`
    - Password: `admin123`
    
    **Teacher Account:**
    - Email: `teacher@scholarsense.com`
    - Password: `teacher123`
    """)
