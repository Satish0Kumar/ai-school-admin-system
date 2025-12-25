"""
Main Streamlit Application
AI-Based Smart School Administration System - Module 1
"""
import streamlit as st
import sys
from pathlib import Path

# Add frontend to path
sys.path.append(str(Path(__file__).resolve().parent))

# Page configuration
st.set_page_config(
    page_title="AI School Admin System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #667eea;
        text-align: center;
        margin-bottom: 0.5rem;
        font-weight: bold;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .stAlert {
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<p class="main-header">🎓 AI School Administration System</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Module 1: Early Warning System for Student Risk Detection</p>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/000000/artificial-intelligence.png", width=80)
    st.title("Navigation")
    
    page = st.radio(
        "Select Module:",
        ["🏠 Home", "🎯 Risk Detection", "📊 About Model"],
        label_visibility="collapsed"
    )
    
    st.divider()
    
    # API Status Check
    from utils.api_client import api_client
    
    st.subheader("System Status")
    
    with st.spinner("Checking API..."):
        is_healthy, response = api_client.health_check()
    
    if is_healthy:
        st.success("✅ API Connected")
        st.caption(f"Version: {response.get('version', 'Unknown')}")
    else:
        st.error("❌ API Offline")
        st.caption("Start with: `python backend/api.py`")
    
    st.divider()
    
    st.caption("© 2025 AI School Admin System")
    st.caption("Module 1 - Version 1.0.0")

# Main content area
if page == "🏠 Home":
    # Home page content
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Model Accuracy",
            value="98.00%",
            delta="Best Model"
        )
    
    with col2:
        st.metric(
            label="Risk Levels",
            value="4 Categories",
            delta="Low to Critical"
        )
    
    with col3:
        st.metric(
            label="Features",
            value="17 Parameters",
            delta="Comprehensive"
        )
    
    st.divider()
    
    # Welcome section
    st.header("Welcome to the Early Warning System")
    
    st.markdown("""
    This AI-powered system helps identify students at risk of academic failure, dropout, 
    or behavioral issues **before** problems escalate.
    
    ### 🎯 Key Features:
    - **Real-time Risk Assessment**: Instant predictions with 98% accuracy
    - **4 Risk Levels**: Low, Medium, High, and Critical classifications
    - **Confidence Scores**: See how confident the model is in each prediction
    - **Intervention Recommendations**: Get actionable suggestions for each student
    - **Batch Processing**: Analyze multiple students simultaneously
    
    ### 📊 How It Works:
    1. Input student demographic, academic, and behavioral data
    2. Our ML model analyzes 17 key features
    3. Get instant risk prediction with confidence scores
    4. Review personalized intervention recommendations
    
    ### 🚀 Get Started:
    Navigate to **🎯 Risk Detection** in the sidebar to begin making predictions.
    """)
    
    # Feature overview
    st.divider()
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📚 Data Categories")
        st.markdown("""
        - **Demographics**: Age, Gender, Grade, SES
        - **Academic**: GPA, Failed Subjects, Assignments
        - **Behavioral**: Incidents, Attendance, Counseling
        - **Engagement**: Library, Extracurricular Activities
        """)
    
    with col2:
        st.subheader("🎓 Model Performance")
        st.markdown("""
        - **Algorithm**: Gradient Boosting Classifier
        - **Accuracy**: 98.00%
        - **Precision**: 98.03%
        - **Recall**: 98.00%
        - **F1-Score**: 98.00%
        """)

elif page == "🎯 Risk Detection":
    # Risk detection page - will be in separate file
    st.info("👉 Navigate to the Risk Detection page to make predictions")
    st.markdown("The Risk Detection interface will be loaded next...")

elif page == "📊 About Model":
    st.header("📊 About the Model")
    
    # Get model info from API
    model_info = api_client.get_model_info()
    
    if model_info:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Model Type", model_info.get('model_name', 'Unknown'))
        with col2:
            st.metric("Accuracy", model_info.get('accuracy', 'N/A'))
        with col3:
            st.metric("Features", model_info.get('features_count', 'N/A'))
        
        st.divider()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Performance Metrics")
            st.markdown(f"""
            - **Precision**: {model_info.get('precision', 'N/A')}
            - **Recall**: {model_info.get('recall', 'N/A')}
            - **F1-Score**: {model_info.get('f1_score', 'N/A')}
            - **Training Date**: {model_info.get('trained_date', 'Unknown')}
            """)
        
        with col2:
            st.subheader("Model Details")
            st.markdown("""
            **Algorithm**: Gradient Boosting Classifier
            
            **Training Data**: 1,000 synthetic student records
            
            **Class Balancing**: SMOTE (Synthetic Minority Over-sampling)
            
            **Feature Scaling**: StandardScaler normalization
            """)
        
        st.divider()
        
        st.subheader("Risk Level Definitions")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.success("**Low Risk (0)**: Student performing well, no intervention needed")
            st.info("**Medium Risk (1)**: Monitor progress, encourage study groups")
        
        with col2:
            st.warning("**High Risk (2)**: Schedule meetings, assign tutors, weekly monitoring")
            st.error("**Critical Risk (3)**: IMMEDIATE intervention, daily monitoring, intensive support")
    
    else:
        st.warning("Unable to fetch model information. Make sure the API is running.")

# Footer
st.divider()
st.caption("AI-Based Smart School Administration System | Module 1: Early Warning System | Version 1.0.0")
