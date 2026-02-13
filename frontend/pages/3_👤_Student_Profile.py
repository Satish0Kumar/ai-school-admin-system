"""
Student Profile - Detailed View
ScholarSense - AI-Powered Academic Intelligence System
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import streamlit as st
from frontend.utils.session_manager import SessionManager
from frontend.utils.api_client import APIClient
import plotly.graph_objects as go
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Student Profile - ScholarSense",
    page_icon="👤",
    layout="wide"
)

# Require authentication
SessionManager.require_auth()

# Apply CSS
st.markdown("""
<style>
    .main { background-color: #f7fafc; padding: 1rem 2rem; }
    .info-box { background: white; padding: 1.5rem; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 2px 8px rgba(0,0,0,0.04); }
    .info-label { color: #4a5568; font-size: 0.85rem; font-weight: 600; text-transform: uppercase; margin-bottom: 0.25rem; }
    .info-value { color: #1a202c; font-size: 1.1rem; font-weight: 700; }
    .section-header { color: #1a202c; font-size: 1.5rem; font-weight: 700; margin: 1.5rem 0 1rem 0; padding-bottom: 0.5rem; border-bottom: 3px solid #2563eb; display: inline-block; }
    .risk-badge { padding: 0.35rem 0.85rem; border-radius: 20px; font-weight: 700; font-size: 0.85rem; display: inline-block; }
    .risk-low { background: #c6f6d5; color: #22543d; border: 2px solid #9ae6b4; }
    .risk-medium { background: #feebc8; color: #7c2d12; border: 2px solid #fbd38d; }
    .risk-high { background: #fed7d7; color: #742a2a; border: 2px solid #fc8181; }
    .risk-critical { background: #feb2b2; color: #742a2a; border: 2px solid #f56565; }
    .stButton > button[kind="primary"] { background: #2563eb !important; color: white !important; }
    [data-testid="stSidebar"] { background-color: white; border-right: 1px solid #e2e8f0; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Get student ID
student_id = st.session_state.get('selected_student_id')
if not student_id:
    st.warning("⚠️ No student selected")
    if st.button("← Back to Students"):
        st.switch_page("pages/2_👥_Students.py")
    st.stop()

# Sidebar
user = SessionManager.get_user()
with st.sidebar:
    st.markdown("### 🎓 ScholarSense")
    st.markdown("---")
    st.markdown(f"""
    <div style="background: #edf2f7; padding: 1rem; border-radius: 10px; border: 1px solid #cbd5e0;">
        <p style="margin: 0; font-weight: 700; color: #1a202c;">{user['full_name']}</p>
        <p style="margin: 0.25rem 0 0 0; color: #4a5568; font-size: 0.9rem;">{user['role'].title()}</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### 📚 Navigation")
    if st.button("📊 Dashboard", use_container_width=True):
        st.switch_page("pages/1_📊_Dashboard.py")
    if st.button("👥 Students", use_container_width=True):
        st.switch_page("pages/2_👥_Students.py")
    if st.button("🎯 Predictions", use_container_width=True):
        st.switch_page("pages/4_🎯_Predictions.py")
    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True, type="primary"):
        SessionManager.logout()
        st.switch_page("app.py")

# Fetch student details
with st.spinner("Loading student details..."):
    details = APIClient.get_student_details(student_id)

if 'error' in details:
    st.error(f"❌ {details['error']}")
    st.stop()

# Header
col1, col2 = st.columns([3, 1])
with col1:
    st.title(f"👤 {details['first_name']} {details['last_name']}")
    st.markdown(f"**Student ID:** {details['student_id']} • **Grade:** {details['grade']}-{details['section']}")

with col2:
    if st.button("← Back to Students", use_container_width=True):
        st.switch_page("pages/2_👥_Students.py")

# Basic Info
st.markdown('<p class="section-header">📋 Basic Information</p>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="info-box">
        <p class="info-label">Age</p>
        <p class="info-value">{details.get('age', 'N/A')}</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="info-box">
        <p class="info-label">Gender</p>
        <p class="info-value">{details.get('gender', 'N/A')}</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="info-box">
        <p class="info-label">Parent</p>
        <p class="info-value">{details.get('parent_name', 'N/A')}</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    status = "🟢 Active" if details.get('is_active', True) else "🔴 Inactive"
    st.markdown(f"""
    <div class="info-box">
        <p class="info-label">Status</p>
        <p class="info-value">{status}</p>
    </div>
    """, unsafe_allow_html=True)

# Academic Performance
st.markdown('<p class="section-header">📚 Academic Performance</p>', unsafe_allow_html=True)

if details.get('academic_records'):
    latest = details['academic_records'][0]
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Current GPA", f"{latest['current_gpa']}%", delta=f"{latest.get('grade_trend', 0):+.1f}%")
    
    with col2:
        st.metric("Failed Subjects", latest.get('failed_subjects', 0))
    
    with col3:
        st.metric("Assignment Rate", f"{latest.get('assignment_submission_rate', 0)}%")
    
    with col4:
        st.metric("Semester", latest.get('semester', 'N/A'))
    
    # Subject scores chart
    if latest.get('math_score'):
        subjects = ['Math', 'Science', 'English', 'Social', 'Language']
        scores = [
            latest.get('math_score', 0),
            latest.get('science_score', 0),
            latest.get('english_score', 0),
            latest.get('social_score', 0),
            latest.get('language_score', 0)
        ]
        
        fig = go.Figure(data=[go.Bar(
            x=subjects,
            y=scores,
            marker_color='#2563eb',
            text=scores,
            textposition='outside'
        )])
        fig.update_layout(
            title="Subject-wise Performance",
            height=350,
            yaxis_title="Score (%)",
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(color='#1a202c')
        )
        st.plotly_chart(fig, use_container_width=True)
else:
    st.info("📭 No academic records found")
    if st.button("➕ Add Academic Record", type="primary"):
        st.session_state['show_academic_form'] = True

# Risk Prediction
st.markdown('<p class="section-header">🎯 Risk Assessment</p>', unsafe_allow_html=True)

if details.get('latest_risk_prediction'):
    pred = details['latest_risk_prediction']
    risk_label = pred['risk_label']
    risk_class = f"risk-{risk_label.lower()}"
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown(f"""
        <div class="info-box" style="text-align: center;">
            <p class="info-label">Current Risk Level</p>
            <p style="font-size: 2rem; margin: 1rem 0;">
                <span class="risk-badge {risk_class}">{risk_label}</span>
            </p>
            <p class="info-value">{pred['confidence_score']:.1f}% Confidence</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Probability chart
        categories = ['Low', 'Medium', 'High', 'Critical']
        probs = [
            pred['probability_low'],
            pred['probability_medium'],
            pred['probability_high'],
            pred['probability_critical']
        ]
        colors = ['#10b981', '#f59e0b', '#ef4444', '#b91c1c']
        
        fig = go.Figure(data=[go.Bar(
            x=categories,
            y=probs,
            marker_color=colors,
            text=[f"{p:.1f}%" for p in probs],
            textposition='outside'
        )])
        fig.update_layout(
            title="Risk Probability Distribution",
            height=300,
            yaxis_title="Probability (%)",
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(color='#1a202c')
        )
        st.plotly_chart(fig, use_container_width=True)
else:
    st.info("📭 No risk prediction available")

# Action buttons
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🎯 Make New Prediction", type="primary", use_container_width=True):
        with st.spinner("Making prediction..."):
            result = APIClient.make_prediction(student_id)
            if 'error' not in result:
                st.success(f"✅ Prediction updated: {result['risk_label']}")
                st.rerun()
            else:
                st.error(f"❌ {result['error']}")

with col2:
    if st.button("📝 Add Academic Record", use_container_width=True):
        st.session_state['show_academic_form'] = True

with col3:
    if st.button("📊 View History", use_container_width=True):
        st.info("Coming soon!")
