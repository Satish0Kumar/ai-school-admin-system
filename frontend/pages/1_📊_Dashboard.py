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

from frontend.utils.ui_helpers import show_skeleton_cards, show_skeleton_table


# ── Imports (add at top with other imports) ────────────────
from frontend.utils.page_header import render_page_header

# Page config
st.set_page_config(
    page_title="Dashboard - ScholarSense",
    page_icon="📊",
    layout="wide"
)


from frontend.utils.sidebar import render_sidebar
render_sidebar()

from frontend.utils.ui_helpers import inject_theme_css
from frontend.utils.ui_helpers import get_plotly_layout
inject_theme_css()



# Require authentication
SessionManager.require_auth()

# ── Show pending toast if any ──────────────────────────────
from frontend.utils.ui_helpers import show_toast
if st.session_state.get('toast_msg'):
    show_toast(
        st.session_state.pop('toast_msg'),
        type=st.session_state.pop('toast_type', 'success')
    )


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

# ── Header ─────────────────────────────────────────────────
user = SessionManager.get_user()
render_page_header(
    title    = "Dashboard",
    subtitle = f"Welcome back, {user['full_name']} 👋 — School-wide overview",
    icon     = "📊",
    section  = "Overview"
)


# ── Global Search ──────────────────────────────────────────
from frontend.utils.global_search import render_global_search

st.markdown('<p class="section-header">🔍 Global Search</p>',
            unsafe_allow_html=True)
render_global_search()
st.markdown("---")



# Show skeleton while loading
skeleton_placeholder = st.empty()
with skeleton_placeholder.container():
    show_skeleton_cards(count=4, cols=4)

# Fetch real data safely
from frontend.utils.ui_helpers import safe_api_call

with st.spinner("Loading dashboard data..."):
    students           = safe_api_call(
                            APIClient.get_students,
                            fallback=[],
                            error_msg="Could not load students"
                         )
    total_students     = len(students)
    high_risk_students = safe_api_call(
                            APIClient.get_high_risk_students,
                            fallback=[],
                            error_msg="Could not load risk data"
                         )

# Clear skeleton once data is ready
skeleton_placeholder.empty()


# Metrics Row
st.markdown("### 📈 Key Metrics")

st.markdown("""
<style>
    /* Stack metric cards on mobile */
    @media (max-width: 640px) {
        div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
            min-width: 48% !important;
            flex: 0 0 48% !important;
        }
    }
</style>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns([1, 1, 1, 1])


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
                **get_plotly_layout(title="", height=350, margin=dict(l=20, r=20, t=20, b=20)),
                showlegend=True,
            )

            fig.update_traces(textposition='outside', marker_line_color='#1e40af', marker_line_width=1.5)
            fig.update_xaxes(showgrid=False)
            fig.update_yaxes(showgrid=True, gridcolor='#f3f4f6')
            st.plotly_chart(fig, width='stretch')

with col_right:
    st.markdown('<p class="section-header">⚠️ Risk Distribution</p>', unsafe_allow_html=True)

    risk_counts = {'Low': 0, 'Medium': 0, 'High': 0, 'Critical': 0}
    for item in high_risk_students:
        label = item.get('prediction', {}).get('risk_label', 'Low')
        risk_counts[label] = risk_counts.get(label, 0) + 1
    risk_counts['Low'] += max(0, total_students - len(high_risk_students))

    fig = go.Figure(data=[go.Pie(
        labels=list(risk_counts.keys()),
        values=list(risk_counts.values()),
        hole=0.45,
        marker_colors=['#10b981', '#f59e0b', '#ef4444', '#b91c1c'],
        textfont=dict(color='white', size=14, family='Arial Black')
    )])
    fig.update_layout(
        **get_plotly_layout(height=350, margin=dict(l=20, r=20, t=20, b=20)),
        showlegend=False,
        xaxis_title="Grade",
        yaxis_title="Number of Students",
    )
    st.plotly_chart(fig, width='stretch')

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
                if st.button("View", key=f"view_{student['id']}", width='stretch'):
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
                if st.button("View", key=f"risk_{student['id']}", width='stretch'):
                    st.session_state['selected_student_id'] = student['id']
                    st.switch_page("pages/3_👤_Student_Profile.py")
            st.markdown("<hr style='margin: 0.5rem 0; border-color: #e2e8f0;'>", unsafe_allow_html=True)
    else:
        st.success("✅ No high-risk students! Excellent work! 🎉")

# ── Activity Feed + Quick Actions ─────────────────────────
st.markdown("<br>", unsafe_allow_html=True)

feed_col, actions_col = st.columns([2, 1])

with feed_col:
    from frontend.utils.activity_log import render_activity_feed
    st.markdown('<p class="section-header">🕐 Recent Activity</p>', unsafe_allow_html=True)
    render_activity_feed(limit=8)

with actions_col:
    st.markdown('<p class="section-header">⚡ Quick Actions</p>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("➕ Add New Student", width='stretch', type="primary"):
        st.switch_page("pages/2_👥_Students.py")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("📋 View All Students", width='stretch'):
        st.switch_page("pages/2_👥_Students.py")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🎯 Make Prediction", width='stretch'):
        st.switch_page("pages/4_🎯_Predictions.py")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("📝 Log Incident", width='stretch'):
        st.switch_page("pages/6_📝_Incident_Logging.py")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔁 Batch Analysis", width='stretch'):
        st.switch_page("pages/10_🔁_Batch_Analysis.py")

