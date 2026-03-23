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
from frontend.utils.ui_helpers import show_empty_state, safe_api_call, show_toast, bulk_action_bar

from frontend.utils.activity_log import log_activity

# Pagination
# PAGE_SIZE is resolved at runtime inside the page, not module level
PAGE_SIZE = 10  # fallback default


@st.cache_data(ttl=300)
def fetch_students_cached(_token, grade=None, section=None, search=None):
    """Cache student list for 5 minutes"""
    if search:
        return APIClient.get_students(search=search)
    return APIClient.get_students(grade=grade, section=section)



# Page config
st.set_page_config(
    page_title="Students - ScholarSense",
    page_icon="👥",
    layout="wide"
)


from frontend.utils.sidebar import render_sidebar
render_sidebar()

from frontend.utils.ui_helpers import inject_theme_css
inject_theme_css()


# Require authentication
SessionManager.require_auth()

# R key → refresh students list
st.markdown("""
<script>
document.addEventListener('keydown', function(e) {
    if (e.key === 'r' && document.activeElement.tagName !== 'INPUT'
                      && document.activeElement.tagName !== 'TEXTAREA') {
        // Click the Streamlit rerun button equivalent
        window.location.reload();
    }
});
</script>
""", unsafe_allow_html=True)



# ── Show pending toast if any ──────────────────────────────
if st.session_state.get('toast_msg'):
    show_toast(
        st.session_state.pop('toast_msg'),
        type=st.session_state.pop('toast_type', 'success')
    )


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

# Reset page to 1 whenever filters change
filter_key = f"{search}_{grade_filter}_{section_filter}"
if st.session_state.get('_last_filter_key') != filter_key:
    st.session_state['page_num'] = 1
    st.session_state['_last_filter_key'] = filter_key


# Fetch students
with st.spinner("Loading students..."):
    grade   = None if grade_filter == "All" else grade_filter
    section = None if section_filter == "All" else section_filter
    token   = st.session_state.get('token', '')


    students = safe_api_call(
        fetch_students_cached,
        fallback = [],
        error_msg = "Could not load students",
        _token  = token,
        grade   = grade,
        section = section,
        search  = search if search else None
    )


# Stats
col1, col2, col3 = st.columns([3, 1, 1])
with col1:
    st.markdown(f'<p class="section-header">📋 Students List ({len(students)} found)</p>', unsafe_allow_html=True)
with col2:
    if SessionManager.is_admin():
        if st.button("➕ Add New Student", type="primary", use_container_width=True):
            st.session_state['show_add_form'] = True
            st.rerun()
with col3:
    bulk_mode = st.toggle("☑️ Bulk Select", key="bulk_mode")

# Init selected set
if 'selected_students' not in st.session_state:
    st.session_state['selected_students'] = set()

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
                        from frontend.utils.activity_log import log_activity
                        log_activity(
                            action="Student Created",
                            entity=f"{first_name} {last_name} ({student_id})",
                            icon="👤",
                            level="success"
                        )
                        st.session_state['show_add_form'] = False
                        st.session_state['toast_msg']  = f"Student {result['student_id']} created successfully!"
                        st.session_state['toast_type'] = 'success'
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error(f"❌ {result['error']}")

# Students list with pagination
if students:
    # ── Pagination calculations ──────────────────────────
    from frontend.utils.preferences import get_pref
    PAGE_SIZE      = get_pref("items_per_page")
    total_students = len(students)
    total_pages    = max(1, -(-total_students // PAGE_SIZE))

    page_num       = st.session_state.get('page_num', 1)
    page_num       = max(1, min(page_num, total_pages))       # clamp within range

    start_idx = (page_num - 1) * PAGE_SIZE
    end_idx   = start_idx + PAGE_SIZE
    page_students = students[start_idx:end_idx]

    # ── Bulk action bar ──────────────────────────────────
    if st.session_state.get('bulk_mode'):
        action = bulk_action_bar(
            selected_ids=st.session_state['selected_students'],
            actions=[
                {"label": "🗑️ Delete Selected",  "key": "bulk_delete",  "type": "primary"},
                {"label": "🎯 Predict All",        "key": "bulk_predict", "type": "secondary"},
                {"label": "📥 Export Selected",    "key": "bulk_export",  "type": "secondary"},
            ]
        )
        if action == "bulk_delete" and st.session_state['selected_students']:
            deleted, failed = 0, 0
            for sid in list(st.session_state['selected_students']):
                r = APIClient.delete_student(sid)
                if 'error' not in r:
                    deleted += 1
                else:
                    failed += 1
            st.session_state['selected_students'] = set()
            st.session_state['toast_msg']  = f"Deleted {deleted} student(s)." + (f" {failed} failed." if failed else "")
            st.session_state['toast_type'] = 'warning'
            st.cache_data.clear()
            st.rerun()

        elif action == "bulk_predict" and st.session_state['selected_students']:
            done = 0
            for sid in st.session_state['selected_students']:
                APIClient.make_prediction(sid)
                done += 1
            show_toast(f"Predictions run for {done} student(s)!", type='success')

        elif action == "bulk_export" and st.session_state['selected_students']:
            import pandas as pd
            selected_data = [s for s in students if s['id'] in st.session_state['selected_students']]
            df = pd.DataFrame(selected_data)
            csv = df.to_csv(index=False)
            st.download_button("📥 Download CSV", csv, "selected_students.csv", "text/csv")

        elif action == "clear":
            st.session_state['selected_students'] = set()
            st.rerun()

    for student in page_students:
        if st.session_state.get('bulk_mode'):
            col0, col1, col2, col3, col4, col5 = st.columns([0.5, 3, 2, 2, 2, 1])
            with col0:
                checked = st.checkbox(
                    "Select",
                    key=f"bulk_{s['id']}",
                    label_visibility="hidden"  # visually hidden but accessible
                )

                if checked:
                    st.session_state['selected_students'].add(student['id'])
                else:
                    st.session_state['selected_students'].discard(student['id'])
        else:
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

    # ── Pagination controls ──────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    p1, p2, p3 = st.columns([1, 2, 1])

    with p1:
        if st.button("⬅️ Previous", use_container_width=True,
                     disabled=(page_num <= 1)):
            st.session_state['page_num'] = page_num - 1
            st.rerun()

    with p2:
        st.markdown(
            f"<p style='text-align:center; font-weight:700; color:#2563eb; "
            f"margin-top:0.5rem;'>Page {page_num} of {total_pages} "
            f"&nbsp;|&nbsp; Showing {start_idx+1}–{min(end_idx, total_students)} "
            f"of {total_students} students</p>",
            unsafe_allow_html=True
        )

    with p3:
        if st.button("Next ➡️", use_container_width=True,
                     disabled=(page_num >= total_pages)):
            st.session_state['page_num'] = page_num + 1
            st.rerun()

else:
    show_empty_state(
        title    = "No Students Found",
        subtitle = "Try adjusting the grade/section filters or search term.",
        icon     = "👥"
    )
