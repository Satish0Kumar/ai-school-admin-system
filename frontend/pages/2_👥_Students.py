"""
Students Management
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
import pandas as pd

# Page config
st.set_page_config(
    page_title="Students - ScholarSense",
    page_icon="👥",
    layout="wide"
)

# Require authentication
SessionManager.require_auth()

# Apply same CSS as dashboard
st.markdown("""
<style>
    .main { background-color: #f7fafc; padding: 1rem 2rem; }
    .section-header { color: #1a202c; font-size: 1.5rem; font-weight: 700; margin: 1.5rem 0 1rem 0; padding-bottom: 0.5rem; border-bottom: 3px solid #2563eb; display: inline-block; }
    .student-card { background: white; padding: 1rem; border-radius: 10px; border: 1px solid #e2e8f0; margin-bottom: 0.75rem; transition: all 0.2s; }
    .student-card:hover { border-color: #2563eb; box-shadow: 0 4px 12px rgba(37, 99, 235, 0.1); }
    .student-name { color: #1a202c; font-weight: 700; font-size: 1.05rem; }
    .student-info { color: #4a5568; font-size: 0.9rem; }
    .stButton > button { border-radius: 8px; font-weight: 600; }
    .stButton > button[kind="primary"] { background: #2563eb !important; color: white !important; border: none !important; }
    .stButton > button[kind="primary"]:hover { background: #1d4ed8 !important; transform: translateY(-2px); box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3) !important; }
    [data-testid="stSidebar"] { background-color: white; border-right: 1px solid #e2e8f0; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Header
user = SessionManager.get_user()
st.title("👥 Students Management")
st.markdown(f"Manage all students • {user['role'].title()}")

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
    if st.button("👥 Students", use_container_width=True, disabled=True):
        pass
    if st.button("🎯 Predictions", use_container_width=True):
        st.switch_page("pages/4_🎯_Predictions.py")
    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True, type="primary"):
        SessionManager.logout()
        st.switch_page("app.py")

# Filters
st.markdown('<p class="section-header">🔍 Filter Students</p>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns([2, 1, 1, 2])

with col1:
    search = st.text_input("🔎 Search by name or ID", placeholder="Search...", label_visibility="collapsed")

with col2:
    grade_filter = st.selectbox("Grade", ["All"] + list(range(6, 11)), key="grade_filter")

with col3:
    section_filter = st.selectbox("Section", ["All", "A", "B", "C"], key="section_filter")

with col4:
    if st.button("🔄 Reset Filters", use_container_width=True):
        st.rerun()

# Fetch students
with st.spinner("Loading students..."):
    grade = None if grade_filter == "All" else grade_filter
    section = None if section_filter == "All" else section_filter
    
    if search:
        students = APIClient.get_students(search=search)
    else:
        students = APIClient.get_students(grade=grade, section=section)

# Stats
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown(f'<p class="section-header">📋 Students List ({len(students)} found)</p>', unsafe_allow_html=True)
with col2:
    if SessionManager.is_admin():
        if st.button("➕ Add New Student", type="primary", use_container_width=True):
            st.session_state['show_add_form'] = True
            st.rerun()

# Add student form
if st.session_state.get('show_add_form', False):
    with st.expander("➕ Add New Student", expanded=True):
        with st.form("add_student_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                student_id = st.text_input("Student ID*", placeholder="STU2026XXX")
                first_name = st.text_input("First Name*", placeholder="John")
                last_name = st.text_input("Last Name*", placeholder="Doe")
                grade = st.selectbox("Grade*", list(range(6, 11)))
                section = st.selectbox("Section", ["A", "B", "C"])
                
            with col2:
                age = st.number_input("Age", min_value=10, max_value=20, value=15)
                gender = st.selectbox("Gender", ["Male", "Female", "Other"])
                parent_name = st.text_input("Parent Name", placeholder="Jane Doe")
                parent_phone = st.text_input("Parent Phone", placeholder="+91-9876543210")
                parent_email = st.text_input("Parent Email", placeholder="parent@email.com")
            
            col1, col2 = st.columns([1, 4])
            with col1:
                submit = st.form_submit_button("Create Student", type="primary", use_container_width=True)
            with col2:
                if st.form_submit_button("Cancel", use_container_width=True):
                    st.session_state['show_add_form'] = False
                    st.rerun()
            
            if submit:
                if not student_id or not first_name or not last_name:
                    st.error("❌ Please fill all required fields")
                else:
                    data = {
                        'student_id': student_id,
                        'first_name': first_name,
                        'last_name': last_name,
                        'grade': grade,
                        'section': section,
                        'age': age,
                        'gender': gender,
                        'parent_name': parent_name,
                        'parent_phone': parent_phone,
                        'parent_email': parent_email
                    }
                    
                    result = APIClient.create_student(data)
                    if 'error' not in result:
                        st.success(f"✅ Student created: {result['student_id']}")
                        st.session_state['show_add_form'] = False
                        st.rerun()
                    else:
                        st.error(f"❌ {result['error']}")

# Students list
if students:
    for student in students:
        col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 1])
        
        with col1:
            st.markdown(f'<p class="student-name">{student["first_name"]} {student["last_name"]}</p>', unsafe_allow_html=True)
            st.markdown(f'<p class="student-info">ID: {student["student_id"]}</p>', unsafe_allow_html=True)
        
        with col2:
            st.markdown(f'<p class="student-info">Grade: {student.get("grade", "N/A")}-{student.get("section", "N/A")}</p>', unsafe_allow_html=True)
            st.markdown(f'<p class="student-info">Age: {student.get("age", "N/A")}</p>', unsafe_allow_html=True)
        
        with col3:
            st.markdown(f'<p class="student-info">Gender: {student.get("gender", "N/A")}</p>', unsafe_allow_html=True)
            st.markdown(f'<p class="student-info">Parent: {student.get("parent_name", "N/A")}</p>', unsafe_allow_html=True)
        
        with col4:
            status = "🟢 Active" if student.get('is_active', True) else "🔴 Inactive"
            st.markdown(f'<p class="student-info">{status}</p>', unsafe_allow_html=True)
        
        with col5:
            if st.button("View", key=f"view_{student['id']}", use_container_width=True):
                st.session_state['selected_student_id'] = student['id']
                st.switch_page("pages/3_👤_Student_Profile.py")
        
        st.markdown("<hr style='margin: 0.5rem 0; border-color: #e2e8f0;'>", unsafe_allow_html=True)
else:
    st.info("📭 No students found matching your criteria")
