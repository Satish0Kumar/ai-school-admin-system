"""
Risk Predictions
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

# Page config
st.set_page_config(
    page_title="Predictions - ScholarSense",
    page_icon="🎯",
    layout="wide"
)

# Require authentication
SessionManager.require_auth()

# Apply CSS
st.markdown("""
<style>
    .main { background-color: #f7fafc; padding: 1rem 2rem; }
    .section-header { color: #1a202c; font-size: 1.5rem; font-weight: 700; margin: 1.5rem 0 1rem 0; padding-bottom: 0.5rem; border-bottom: 3px solid #2563eb; display: inline-block; }
    .risk-badge { padding: 0.35rem 0.85rem; border-radius: 20px; font-weight: 700; font-size: 0.85rem; display: inline-block; }
    .risk-low { background: #c6f6d5; color: #22543d; border: 2px solid #9ae6b4; }
    .risk-medium { background: #feebc8; color: #7c2d12; border: 2px solid #fbd38d; }
    .risk-high { background: #fed7d7; color: #742a2a; border: 2px solid #fc8181; }
    .risk-critical { background: #feb2b2; color: #742a2a; border: 2px solid #f56565; }
    .student-name { color: #1a202c; font-weight: 700; font-size: 1.05rem; }
    .stButton > button[kind="primary"] { background: #2563eb !important; color: white !important; }
    [data-testid="stSidebar"] { background-color: white; border-right: 1px solid #e2e8f0; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Header
user = SessionManager.get_user()
st.title("🎯 Risk Predictions")
st.markdown("Monitor and predict student dropout risk")

# Sidebar
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
    if st.button("🎯 Predictions", use_container_width=True, disabled=True):
        pass
    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True, type="primary"):
        SessionManager.logout()
        st.switch_page("app.py")

# Filters
col1, col2 = st.columns([1, 3])
with col1:
    grade_filter = st.selectbox("Filter by Grade", ["All"] + list(range(6, 11)))

# Fetch high-risk students
with st.spinner("Loading predictions..."):
    grade = None if grade_filter == "All" else grade_filter
    high_risk = APIClient.get_high_risk_students(grade=grade)

# High-risk students
st.markdown(f'<p class="section-header">🚨 High-Risk Students ({len(high_risk)} found)</p>', unsafe_allow_html=True)

if high_risk:
    for item in high_risk:
        student = item['student']
        pred = item['prediction']
        risk_label = pred['risk_label']
        risk_class = f"risk-{risk_label.lower()}"
        
        col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 1])
        
        with col1:
            st.markdown(f'<p class="student-name">{student["first_name"]} {student["last_name"]}</p>', unsafe_allow_html=True)
            st.markdown(f'<p style="color: #4a5568; font-size: 0.9rem;">ID: {student["student_id"]}</p>', unsafe_allow_html=True)
        
        with col2:
            st.markdown(f'<p style="color: #4a5568;">Grade: {student.get("grade", "N/A")}-{student.get("section", "N/A")}</p>', unsafe_allow_html=True)
        
        with col3:
            st.markdown(f'<span class="risk-badge {risk_class}">{risk_label}</span>', unsafe_allow_html=True)
        
        with col4:
            st.markdown(f'<p style="color: #4a5568;">Confidence: {pred["confidence_score"]:.1f}%</p>', unsafe_allow_html=True)
        
        with col5:
            if st.button("View", key=f"view_{student['id']}", use_container_width=True):
                st.session_state['selected_student_id'] = student['id']
                st.switch_page("pages/3_👤_Student_Profile.py")
        
        st.markdown("<hr style='margin: 0.5rem 0; border-color: #e2e8f0;'>", unsafe_allow_html=True)
else:
    st.success("✅ No high-risk students found! Excellent work! 🎉")

# Make prediction section
st.markdown('<p class="section-header">🎯 Make New Prediction</p>', unsafe_allow_html=True)

students = APIClient.get_students()
if students:
    student_options = {f"{s['first_name']} {s['last_name']} ({s['student_id']})": s['id'] for s in students}
    
    col1, col2 = st.columns([3, 1])
    with col1:
        selected = st.selectbox("Select Student", list(student_options.keys()))
    with col2:
        if st.button("🎯 Predict", type="primary", use_container_width=True):
            student_id = student_options[selected]
            with st.spinner("Making prediction..."):
                result = APIClient.make_prediction(student_id)
                if 'error' not in result:
                    st.success(f"✅ Prediction: {result['risk_label']} ({result['confidence_score']:.1f}% confidence)")
                    st.balloons()
                    st.rerun()
                else:
                    st.error(f"❌ {result['error']}")
