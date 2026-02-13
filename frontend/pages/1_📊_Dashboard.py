"""
Dashboard - Main Overview
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
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Page config
st.set_page_config(
    page_title="Dashboard - ScholarSense",
    page_icon="📊",
    layout="wide"
)

# Require authentication
SessionManager.require_auth()

# Professional CSS with HIGH CONTRAST
st.markdown("""
<style>
    /* Clean light background */
    .main {
        background-color: #f7fafc;
        padding: 1rem 2rem;
    }
    
    /* Metric cards - white with borders */
    .metric-card {
        background: white;
        padding: 1.75rem;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        text-align: center;
        transition: all 0.2s;
    }
    
    .metric-card:hover {
        border-color: #cbd5e0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        transform: translateY(-2px);
    }
    
    .metric-value {
        font-size: 2.75rem;
        font-weight: 800;
        color: #2563eb;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        font-size: 1rem;
        color: #4a5568;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Section headers */
    .section-header {
        color: #1a202c;
        font-size: 1.5rem;
        font-weight: 700;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #2563eb;
        display: inline-block;
    }
    
    /* Risk badges */
    .risk-badge {
        padding: 0.35rem 0.85rem;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.85rem;
        display: inline-block;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .risk-low { 
        background: #c6f6d5; 
        color: #22543d;
        border: 2px solid #9ae6b4;
    }
    
    .risk-medium { 
        background: #feebc8; 
        color: #7c2d12;
        border: 2px solid #fbd38d;
    }
    
    .risk-high { 
        background: #fed7d7; 
        color: #742a2a;
        border: 2px solid #fc8181;
    }
    
    .risk-critical { 
        background: #feb2b2; 
        color: #742a2a;
        border: 2px solid #f56565;
    }
    
    /* Student cards */
    .student-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #e2e8f0;
        margin-bottom: 0.75rem;
        transition: all 0.2s;
    }
    
    .student-card:hover {
        border-color: #2563eb;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.1);
    }
    
    .student-name {
        color: #1a202c;
        font-weight: 700;
        font-size: 1.05rem;
    }
    
    .student-grade {
        color: #4a5568;
        font-size: 0.95rem;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: white;
        border-right: 1px solid #e2e8f0;
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
        color: #1a202c;
    }
    
    /* Buttons */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        border: 2px solid #e2e8f0;
        transition: all 0.2s;
    }
    
    .stButton > button:hover {
        border-color: #2563eb;
        color: #2563eb;
    }
    
    .stButton > button[kind="primary"] {
        background: #2563eb !important;
        color: white !important;
        border: none !important;
    }
    
    .stButton > button[kind="primary"]:hover {
        background: #1d4ed8 !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3) !important;
    }
    
    /* Charts */
    .plot-container {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Header
user = SessionManager.get_user()
col1, col2 = st.columns([3, 1])
with col1:
    st.title("📊 Dashboard")
    st.markdown(f"Welcome back, **{user['full_name']}** • {user['role'].title()} 👋")

# Sidebar
with st.sidebar:
    st.markdown("### 🎓 ScholarSense")
    st.markdown("---")
    
    # User info card
    st.markdown(f"""
    <div style="background: #edf2f7; padding: 1rem; border-radius: 10px; border: 1px solid #cbd5e0;">
        <p style="margin: 0; font-weight: 700; color: #1a202c; font-size: 1.05rem;">{user['full_name']}</p>
        <p style="margin: 0.25rem 0 0 0; color: #4a5568; font-size: 0.9rem;">{user['role'].title()}</p>
        <p style="margin: 0.25rem 0 0 0; color: #718096; font-size: 0.85rem;">📧 {user['email']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Navigation
    st.markdown("### 📚 Navigation")
    if st.button("📊 Dashboard", use_container_width=True, disabled=True):
        pass
    if st.button("👥 Students", use_container_width=True):
        st.switch_page("pages/2_👥_Students.py")
    if st.button("🎯 Predictions", use_container_width=True):
        st.switch_page("pages/4_🎯_Predictions.py")
    
    st.markdown("---")
    
    if st.button("🚪 Logout", use_container_width=True, type="primary"):
        SessionManager.logout()
        st.switch_page("app.py")

# Fetch data
with st.spinner("Loading dashboard data..."):
    students = APIClient.get_students()
    total_students = len(students)
    high_risk_students = APIClient.get_high_risk_students()

# Metrics Row
st.markdown("### 📈 Key Metrics")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{total_students}</div>
        <div class="metric-label">👥 Total Students</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    active_students = len([s for s in students if s.get('is_active', True)])
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value" style="color: #10b981;">{active_students}</div>
        <div class="metric-label">✅ Active Students</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    high_risk_count = len(high_risk_students)
    color = "#ef4444" if high_risk_count > 0 else "#10b981"
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value" style="color: {color};">{high_risk_count}</div>
        <div class="metric-label">⚠️ High-Risk</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    grades = [s.get('grade') for s in students if s.get('grade')]
    unique_grades = len(set(grades)) if grades else 0
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value" style="color: #8b5cf6;">{unique_grades}</div>
        <div class="metric-label">📚 Grades</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Charts Row
col_left, col_right = st.columns([2, 1])

with col_left:
    st.markdown('<p class="section-header">📊 Students by Grade</p>', unsafe_allow_html=True)
    
    if students:
        grade_data = {}
        for student in students:
            grade = student.get('grade')
            if grade:
                grade_data[grade] = grade_data.get(grade, 0) + 1
        
        if grade_data:
            df_grades = pd.DataFrame(list(grade_data.items()), columns=['Grade', 'Count'])
            df_grades = df_grades.sort_values('Grade')
            
            fig = px.bar(
                df_grades,
                x='Grade',
                y='Count',
                color='Count',
                color_continuous_scale=[[0, '#dbeafe'], [1, '#2563eb']],
                text='Count'
            )
            fig.update_layout(
                showlegend=False,
                height=350,
                margin=dict(l=20, r=20, t=20, b=20),
                xaxis_title="Grade",
                yaxis_title="Number of Students",
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(color='#1a202c', size=12)
            )
            fig.update_traces(textposition='outside', marker_line_color='#1e40af', marker_line_width=1.5)
            fig.update_xaxes(showgrid=False)
            fig.update_yaxes(showgrid=True, gridcolor='#f3f4f6')
            st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.markdown('<p class="section-header">⚠️ Risk Distribution</p>', unsafe_allow_html=True)
    
    if students:
        risk_counts = {'Low': 0, 'Medium': 0, 'High': 0, 'Critical': 0}
        
        for student in students[:10]:
            details = APIClient.get_student_details(student['id'])
            if details and 'latest_risk_prediction' in details and details['latest_risk_prediction']:
                risk_label = details['latest_risk_prediction'].get('risk_label', 'Low')
                risk_counts[risk_label] = risk_counts.get(risk_label, 0) + 1
        
        fig = go.Figure(data=[go.Pie(
            labels=list(risk_counts.keys()),
            values=list(risk_counts.values()),
            hole=0.45,
            marker_colors=['#10b981', '#f59e0b', '#ef4444', '#b91c1c'],
            textfont=dict(color='white', size=14, family='Arial Black')
        )])
        fig.update_layout(
            showlegend=True,
            height=350,
            margin=dict(l=20, r=20, t=20, b=20),
            paper_bgcolor='white',
            font=dict(color='#1a202c', size=12)
        )
        st.plotly_chart(fig, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# Students & Alerts Row
col1, col2 = st.columns(2)

with col1:
    st.markdown('<p class="section-header">👥 Recent Students</p>', unsafe_allow_html=True)
    
    if students:
        for student in students[:5]:
            col_a, col_b, col_c = st.columns([4, 2, 1])
            with col_a:
                st.markdown(f'<p class="student-name">{student["first_name"]} {student["last_name"]}</p>', unsafe_allow_html=True)
            with col_b:
                st.markdown(f'<p class="student-grade">Grade {student.get("grade", "N/A")}-{student.get("section", "N/A")}</p>', unsafe_allow_html=True)
            with col_c:
                if st.button("View", key=f"view_{student['id']}", use_container_width=True):
                    st.session_state['selected_student_id'] = student['id']
                    st.switch_page("pages/3_👤_Student_Profile.py")
            st.markdown("<hr style='margin: 0.5rem 0; border-color: #e2e8f0;'>", unsafe_allow_html=True)

with col2:
    st.markdown('<p class="section-header">🚨 High-Risk Alerts</p>', unsafe_allow_html=True)
    
    if high_risk_students:
        for item in high_risk_students[:5]:
            student = item['student']
            prediction = item['prediction']
            risk_label = prediction['risk_label']
            risk_class = f"risk-{risk_label.lower()}"
            
            col_a, col_b, col_c = st.columns([4, 2, 1])
            with col_a:
                st.markdown(f'<p class="student-name">{student["first_name"]} {student["last_name"]}</p>', unsafe_allow_html=True)
            with col_b:
                st.markdown(f'<span class="risk-badge {risk_class}">{risk_label}</span>', unsafe_allow_html=True)
            with col_c:
                if st.button("View", key=f"risk_{student['id']}", use_container_width=True):
                    st.session_state['selected_student_id'] = student['id']
                    st.switch_page("pages/3_👤_Student_Profile.py")
            st.markdown("<hr style='margin: 0.5rem 0; border-color: #e2e8f0;'>", unsafe_allow_html=True)
    else:
        st.success("✅ No high-risk students! Excellent work! 🎉")

# Quick Actions
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<p class="section-header">⚡ Quick Actions</p>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("➕ Add New Student", use_container_width=True, type="primary"):
        st.switch_page("pages/2_👥_Students.py")

with col2:
    if st.button("📋 View All Students", use_container_width=True):
        st.switch_page("pages/2_👥_Students.py")

with col3:
    if st.button("🎯 Make Prediction", use_container_width=True):
        st.switch_page("pages/4_🎯_Predictions.py")
