"""
Parent Communication Portal
ScholarSense - AI-Powered Academic Intelligence System
Enhancement 9: Send emails, view history, manage templates
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from frontend.utils.session_manager import SessionManager

# ============================================
# PAGE CONFIG
# ============================================
st.set_page_config(
    page_title="Parent Portal - ScholarSense",
    page_icon="📧",
    layout="wide"
)


from frontend.utils.sidebar import render_sidebar
render_sidebar()

from frontend.utils.ui_helpers import inject_theme_css
from frontend.utils.ui_helpers import get_plotly_layout
inject_theme_css()

# ============================================
# SESSION CHECK
# ============================================
SessionManager.require_auth()

# ============================================
# STYLES
# ============================================
st.markdown("""
<style>
    .main { background-color: #f7fafc; padding: 1rem 2rem; }
    .section-header {
        color: #1a202c; font-size: 1.3rem; font-weight: 700;
        margin: 1.5rem 0 1rem 0; padding-bottom: 0.4rem;
        border-bottom: 3px solid #2563eb; display: inline-block;
    }
    .kpi-card {
        background: white; padding: 1.3rem 1rem;
        border-radius: 14px; border: 1px solid #e2e8f0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        text-align: center; margin-bottom: 1rem;
    }
    .kpi-value {
        font-size: 2rem; font-weight: 800; margin: 0.2rem 0;
    }
    .kpi-label {
        font-size: 0.8rem; color: #4a5568; font-weight: 600;
        text-transform: uppercase; letter-spacing: 0.04em;
    }
    .template-card {
        background: white; padding: 1.2rem 1.5rem;
        border-radius: 12px; border: 1px solid #e2e8f0;
        border-left: 5px solid #2563eb;
        box-shadow: 0 2px 6px rgba(0,0,0,0.04);
        margin-bottom: 1rem;
    }
    .email-preview {
        background: #f8faff; padding: 1.5rem;
        border-radius: 10px; border: 1px solid #c3dafe;
        font-family: Arial, sans-serif;
        font-size: 0.9rem; line-height: 1.7;
        white-space: pre-wrap; color: #1a202c;
    }
    .status-sent   { color: #00CC44; font-weight: 700; }
    .status-failed { color: #FF4B4B; font-weight: 700; }
    [data-testid="stSidebar"] {
        background-color: white; border-right: 1px solid #e2e8f0;
    }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ============================================
# CONSTANTS
# ============================================
API_BASE = "http://localhost:5000/api"

COMM_TYPES = [
    'Risk Alert', 'Academic Warning',
    'Behavioral Notice', 'General Update',
    'Attendance Alert', 'Marks Report', 'Custom'
]

COMM_TYPE_ICONS = {
    'Risk Alert':        '🚨',
    'Academic Warning':  '📚',
    'Behavioral Notice': '📋',
    'General Update':    '🏫',
    'Attendance Alert':  '🗓️',
    'Marks Report':      '📊',
    'Custom':            '✍️'
}

SEMESTERS = [
    '2025-2026 Sem 1', '2025-2026 Sem 2',
    '2024-2025 Sem 1', '2024-2025 Sem 2'
]

GRADES = [6, 7, 8, 9, 10]

# ============================================
# API HELPERS
# ============================================
def get_headers():
    return {"Authorization": f"Bearer {st.session_state.get('token', '')}"}

def api_get(endpoint, params=None):
    try:
        r = requests.get(
            f"{API_BASE}{endpoint}",
            headers=get_headers(),
            params=params,
            timeout=15
        )
        return r.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}

def api_post(endpoint, payload):
    try:
        r = requests.post(
            f"{API_BASE}{endpoint}",
            headers=get_headers(),
            json=payload,
            timeout=30
        )
        return r.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_all_students():
    """Fetch all active students"""
    res = api_get("/students")
    return res if isinstance(res, list) else []

def get_at_risk_students():
    """Fetch Critical + High risk students from batch predictions"""
    res = api_get("/batch/predictions", params={"limit": 500})
    if res.get('status') == 'success':
        students = res['data'].get('students', [])
        return [
            s for s in students
            if s.get('risk_label') in ('Critical', 'High')
        ]
    return []

def preview_template(comm_type, student, extra_data={}):
    """
    Client-side preview of template
    (mirrors backend build_message logic)
    """
    previews = {
        'Risk Alert': (
            f"⚠️ Risk Alert: {student.get('first_name', '')} "
            f"{student.get('last_name', '')} Needs Your Attention\n\n"
            f"Dear {student.get('parent_name', 'Parent/Guardian')},\n\n"
            f"Our system has identified your child as being at "
            f"{extra_data.get('risk_label', 'High')} Risk.\n\n"
            f"GPA: {extra_data.get('gpa', 'N/A')}% | "
            f"Failed Subjects: {extra_data.get('failed_subjects', 'N/A')}\n\n"
            f"Please contact the school to discuss a support plan.\n\n"
            f"Warm regards,\nScholarSense"
        ),
        'Academic Warning': (
            f"📚 Academic Warning for "
            f"{student.get('first_name', '')} "
            f"{student.get('last_name', '')}\n\n"
            f"Dear {student.get('parent_name', 'Parent/Guardian')},\n\n"
            f"Current GPA: {extra_data.get('gpa', 'N/A')}% | "
            f"Failed: {extra_data.get('failed_subjects', 0)} subjects\n\n"
            f"Please review your child's study schedule "
            f"and schedule a parent-teacher meeting.\n\n"
            f"Warm regards,\nScholarSense"
        ),
        'Behavioral Notice': (
            f"📋 Behavioral Notice for "
            f"{student.get('first_name', '')} "
            f"{student.get('last_name', '')}\n\n"
            f"Dear {student.get('parent_name', 'Parent/Guardian')},\n\n"
            f"A behavioral incident has been recorded. "
            f"Please contact the class teacher for details.\n\n"
            f"Warm regards,\nScholarSense"
        ),
        'Attendance Alert': (
            f"🗓️ Attendance Alert: "
            f"{student.get('first_name', '')} "
            f"{student.get('last_name', '')}\n\n"
            f"Dear {student.get('parent_name', 'Parent/Guardian')},\n\n"
            f"We are concerned about your child's attendance. "
            f"Please ensure regular school attendance.\n\n"
            f"Warm regards,\nScholarSense"
        ),
        'Marks Report': (
            f"📊 Marks Report: "
            f"{student.get('first_name', '')} "
            f"{student.get('last_name', '')} — "
            f"{extra_data.get('semester', 'Current Semester')}\n\n"
            f"Dear {student.get('parent_name', 'Parent/Guardian')},\n\n"
            f"GPA: {extra_data.get('gpa', 'N/A')}% | "
            f"Total: {extra_data.get('total_marks', 'N/A')}/500 | "
            f"Failed: {extra_data.get('failed_subjects', 0)}\n\n"
            f"Warm regards,\nScholarSense"
        ),
        'General Update': (
            f"🏫 Update Regarding "
            f"{student.get('first_name', '')} "
            f"{student.get('last_name', '')}\n\n"
            f"Dear {student.get('parent_name', 'Parent/Guardian')},\n\n"
            f"{extra_data.get('custom_message', '[Your message here]')}\n\n"
            f"Warm regards,\nScholarSense"
        ),
        'Custom': (
            f"Subject: {extra_data.get('custom_subject', '[Custom Subject]')}\n\n"
            f"{extra_data.get('custom_message', '[Your custom message here]')}"
        )
    }
    return previews.get(comm_type, "Preview not available")

# ============================================
# SIDEBAR
# ============================================
user = SessionManager.get_user()
with st.sidebar:
    st.markdown("### 🎓 ScholarSense")
    st.markdown("---")
    st.markdown(f"""
    <div style="background:#edf2f7; padding:1rem; border-radius:10px;
                border:1px solid #cbd5e0;">
        <p style="margin:0; font-weight:700;
                  color:#1a202c;">{user['full_name']}</p>
        <p style="margin:0.25rem 0 0 0; color:#4a5568;
                  font-size:0.9rem;">{user['role'].title()}</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### 📚 Navigation")
    if st.button("📊 Dashboard",            width='stretch'):
        st.switch_page("pages/1_📊_Dashboard.py")
    if st.button("👥 Students",             width='stretch'):
        st.switch_page("pages/2_👥_Students.py")
    if st.button("🔁 Batch Analysis",       width='stretch'):
        st.switch_page("pages/10_🔁_Batch_Analysis.py")
    if st.button("📝 Incident Logging",     width='stretch'):
        st.switch_page("pages/6_📝_Incident_Logging.py")
    if st.button("📝 Marks Entry",          width='stretch'):
        st.switch_page("pages/9_📝_Marks_Entry.py")
    st.markdown("---")
    if st.button("🚪 Logout", width='stretch', type="primary"):
        SessionManager.logout()
        st.switch_page("app.py")

# ============================================
# PAGE HEADER
# ============================================
st.markdown("""
    <h1 style='color:#1a202c; margin-bottom:0;'>📧 Parent Communication Portal</h1>
    <p style='color:#4a5568; margin-top:0.25rem;'>
        Send email notifications to parents, track history
        and manage communication templates
    </p>
    <hr style='border:none; border-top:1px solid #e2e8f0; margin:1rem 0;'/>
""", unsafe_allow_html=True)

# ============================================
# QUICK STATS ROW
# ============================================
with st.spinner(""):
    stats_res = api_get("/communications/stats")

if stats_res.get('status') == 'success':
    stats = stats_res['data']
    qc1, qc2, qc3, qc4 = st.columns(4)

    with qc1:
        st.markdown(f"""
        <div class="kpi-card" style="border-top:4px solid #2563eb;">
            <p class="kpi-label">📧 Total Emails Sent</p>
            <p class="kpi-value" style="color:#2563eb;">
                {stats.get('total', 0)}
            </p>
        </div>
        """, unsafe_allow_html=True)

    with qc2:
        sent_count = next(
            (x['count'] for x in stats.get('by_status', [])
             if x['status'] == 'sent'), 0
        )
        st.markdown(f"""
        <div class="kpi-card" style="border-top:4px solid #00CC44;">
            <p class="kpi-label">✅ Successfully Sent</p>
            <p class="kpi-value" style="color:#00CC44;">{sent_count}</p>
        </div>
        """, unsafe_allow_html=True)

    with qc3:
        failed_count = next(
            (x['count'] for x in stats.get('by_status', [])
             if x['status'] == 'failed'), 0
        )
        st.markdown(f"""
        <div class="kpi-card" style="border-top:4px solid #FF4B4B;">
            <p class="kpi-label">❌ Failed</p>
            <p class="kpi-value" style="color:#FF4B4B;">{failed_count}</p>
        </div>
        """, unsafe_allow_html=True)

    with qc4:
        st.markdown(f"""
        <div class="kpi-card" style="border-top:4px solid #FFA500;">
            <p class="kpi-label">📅 Last 7 Days</p>
            <p class="kpi-value" style="color:#FFA500;">
                {stats.get('last_week', 0)}
            </p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# ============================================
# TABS
# ============================================
tab1, tab2, tab3 = st.tabs([
    "📤 Send Email",
    "📋 History",
    "📄 Templates"
])


# ============================================================
# TAB 1 — SEND EMAIL
# ============================================================
with tab1:
    st.markdown("### 📤 Send Email to Parent")
    st.markdown("---")

    # ── Send Mode Toggle ───────────────────────────────────
    send_mode = st.radio(
        "📌 Send Mode",
        options=["Single Student", "Batch — All At-Risk Students"],
        horizontal=True
    )

    st.markdown("---")

    # ============================================================
    # SINGLE SEND
    # ============================================================
    if send_mode == "Single Student":

        # ── Step 1: Select Student ─────────────────────────
        st.markdown("#### 👤 Step 1 — Select Student")

        with st.spinner("Loading students..."):
            all_students = get_all_students()

        if not all_students:
            st.warning("⚠️ Could not load students. Check API.")
            st.stop()

        student_options = {
            f"{s['student_id']} — {s['first_name']} {s['last_name']} "
            f"(Grade {s['grade']}{s.get('section', '')})": s
            for s in all_students
        }

        s1c1, s1c2 = st.columns([3, 1])
        with s1c1:
            sel_label = st.selectbox(
                "👤 Select Student",
                options=list(student_options.keys())
            )
        with s1c2:
            sel_student = student_options[sel_label]
            parent_email = sel_student.get('parent_email', '')
            st.markdown("<br/>", unsafe_allow_html=True)
            if parent_email:
                st.success(f"📧 {parent_email}")
            else:
                st.error("❌ No parent email on file")

        st.markdown("---")

        # ── Step 2: Select Template ────────────────────────
        st.markdown("#### 📋 Step 2 — Select Communication Type")

        t1c1, t1c2 = st.columns(2)
        with t1c1:
            sel_comm_type = st.selectbox(
                "📌 Communication Type",
                options=COMM_TYPES,
                format_func=lambda x: f"{COMM_TYPE_ICONS.get(x, '')} {x}"
            )

        # Extra data based on type
        extra_data      = {}
        custom_subject  = None
        custom_message  = None

        with t1c2:
            if sel_comm_type in ('Risk Alert', 'Academic Warning', 'Marks Report'):
                extra_data['gpa'] = st.number_input(
                    "📊 Student GPA (%)",
                    min_value=0.0, max_value=100.0,
                    value=50.0, step=0.5
                )

        # Additional fields per type
        if sel_comm_type in ('Risk Alert', 'Academic Warning'):
            ex1, ex2 = st.columns(2)
            with ex1:
                extra_data['risk_label'] = st.selectbox(
                    "⚠️ Risk Level",
                    options=['Low', 'Medium', 'High', 'Critical'],
                    index=2
                )
            with ex2:
                extra_data['failed_subjects'] = st.number_input(
                    "❌ Failed Subjects",
                    min_value=0, max_value=5, value=0
                )

        if sel_comm_type in ('Marks Report', 'Academic Warning'):
            extra_data['semester'] = st.selectbox(
                "📅 Semester", options=SEMESTERS
            )

        if sel_comm_type == 'Marks Report':
            extra_data['total_marks'] = st.number_input(
                "🔢 Total Marks (/500)",
                min_value=0.0, max_value=500.0,
                value=250.0, step=0.5
            )

        if sel_comm_type in ('General Update', 'Custom'):
            if sel_comm_type == 'Custom':
                custom_subject = st.text_input(
                    "📌 Email Subject *",
                    placeholder="Enter custom email subject..."
                )
            custom_message = st.text_area(
                "✍️ Message Body *",
                placeholder="Enter your custom message...",
                height=150
            )
            if custom_message:
                extra_data['custom_message'] = custom_message
            if custom_subject:
                extra_data['custom_subject'] = custom_subject

        st.markdown("---")

        # ── Step 3: Preview ────────────────────────────────
        st.markdown("#### 👁️ Step 3 — Preview Email")

        with st.expander("📬 Click to Preview Email", expanded=True):
            preview_text = preview_template(
                sel_comm_type, sel_student, extra_data
            )
            st.markdown(
                f'<div class="email-preview">{preview_text}</div>',
                unsafe_allow_html=True
            )

        st.markdown("---")

        # ── Step 4: Send ───────────────────────────────────
        st.markdown("#### 📤 Step 4 — Send")

        if not parent_email:
            st.error(
                "❌ Cannot send — no parent email on file for this student. "
                "Update the student record first."
            )
        else:
            # Validate custom fields
            can_send = True
            if sel_comm_type == 'Custom' and not custom_subject:
                st.warning("⚠️ Please enter a custom subject.")
                can_send = False
            if sel_comm_type in ('Custom', 'General Update') \
               and not custom_message:
                st.warning("⚠️ Please enter a message body.")
                can_send = False

            if can_send:
                send_btn = st.button(
                    f"📤 Send Email to {parent_email}",
                    width='stretch',
                    type="primary"
                )

                if send_btn:
                    payload = {
                        'student_id':        sel_student['id'],
                        'communication_type': sel_comm_type,
                        'extra_data':        extra_data
                    }
                    if custom_subject:
                        payload['custom_subject'] = custom_subject
                    if custom_message:
                        payload['custom_message'] = custom_message

                    with st.spinner(
                        f"📤 Sending email to {parent_email}..."
                    ):
                        result = api_post("/communications/send", payload)

                    if result.get('status') == 'success':
                        st.success(
                            f"✅ Email sent successfully to "
                            f"**{parent_email}**!"
                        )
                        st.balloons()

                        # Show confirmation card
                        rec = result['data']
                        st.markdown(f"""
                        <div style='background:#f0fff4; padding:1rem 1.5rem;
                                    border-radius:10px;
                                    border-left:5px solid #00CC44;
                                    margin-top:1rem;'>
                            <b>📧 Email Confirmation</b><br/>
                            📌 Type: <b>{rec.get('communication_type')}</b>
                            &nbsp;|&nbsp;
                            📧 To: <b>{rec.get('parent_email')}</b>
                            &nbsp;|&nbsp;
                            ✅ Status: <b>{rec.get('status').upper()}</b><br/>
                            🕐 Sent at:
                            <b>{rec.get('sent_at', 'Just now')}</b>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.error(
                            f"❌ Failed to send: "
                            f"{result.get('message', 'Unknown error')}"
                        )

    # ============================================================
    # BATCH SEND
    # ============================================================
    else:
        st.markdown("#### 🚨 Batch Send — At-Risk Students")
        st.markdown(
            "This will send emails to parents of all "
            "**Critical** and **High** risk students."
        )
        st.markdown("---")

        with st.spinner("Loading at-risk students..."):
            at_risk = get_at_risk_students()

        if not at_risk:
            st.info(
                "ℹ️ No Critical or High risk students found. "
                "Run batch predictions first."
            )
        else:
            # Show at-risk students
            st.markdown(
                f"**{len(at_risk)} at-risk student(s) identified:**"
            )

            risk_rows = []
            for s in at_risk:
                risk_rows.append({
                    'Student':     s.get('student_name'),
                    'ID':          s.get('student_code'),
                    'Grade':       f"{s.get('grade')}{s.get('section', '')}",
                    'Risk Level':  s.get('risk_label'),
                    'Parent Email':s.get('parent_email', '❌ No email')
                })

            risk_df = pd.DataFrame(risk_rows)
            st.dataframe(risk_df, width='stretch', hide_index=True)

            st.markdown("---")

            # Batch config
            bc1, bc2 = st.columns(2)
            with bc1:
                batch_comm_type = st.selectbox(
                    "📌 Email Type to Send",
                    options=['Risk Alert', 'Academic Warning', 'General Update'],
                    format_func=lambda x: (
                        f"{COMM_TYPE_ICONS.get(x, '')} {x}"
                    )
                )
            with bc2:
                batch_semester = st.selectbox(
                    "📅 Semester", options=SEMESTERS
                )

            batch_extra = {
                'semester': batch_semester,
                'risk_label': 'High'
            }

            st.markdown("---")
            st.warning(
                f"⚠️ This will send **{len(at_risk)} emails** "
                f"to parents. This action cannot be undone."
            )

            batch_btn = st.button(
                f"🚀 Send {batch_comm_type} to All {len(at_risk)} At-Risk Parents",
                width='stretch',
                type="primary"
            )

            if batch_btn:
                student_ids = [
                    s['student_id'] for s in at_risk
                    if s.get('parent_email')
                ]

                if not student_ids:
                    st.error(
                        "❌ None of the at-risk students "
                        "have parent emails on file."
                    )
                else:
                    progress = st.progress(
                        0, text="📤 Sending batch emails..."
                    )

                    with st.spinner(
                        f"Sending {len(student_ids)} emails..."
                    ):
                        payload = {
                            'student_ids':       student_ids,
                            'communication_type': batch_comm_type,
                            'extra_data':        batch_extra
                        }
                        batch_result = api_post(
                            "/communications/batch", payload
                        )
                        progress.progress(100, text="✅ Done!")

                    if batch_result.get('status') == 'success':
                        bd = batch_result['data']
                        st.success(
                            f"✅ Batch complete! "
                            f"**{bd['sent']}** sent | "
                            f"**{bd['failed']}** failed"
                        )
                        if bd['sent'] > 0:
                            st.balloons()

                        # Results breakdown
                        results_df = pd.DataFrame([{
                            'Student ID': r['student_id'],
                            'Status':     r['status'].upper(),
                            'Note':       r.get('message', '✅ Sent')
                        } for r in bd.get('results', [])])

                        st.dataframe(
                            results_df,
                            width='stretch',
                            hide_index=True
                        )
                    else:
                        st.error(
                            f"❌ Batch failed: "
                            f"{batch_result.get('message', 'Unknown error')}"
                        )


# ============================================================
# TAB 2 — HISTORY
# ============================================================
with tab2:
    st.markdown("### 📋 Communication History")
    st.markdown("All emails sent to parents, with delivery status.")
    st.markdown("---")

    # ── Filters ───────────────────────────────────────────
    hf1, hf2, hf3, hf4, hf5 = st.columns(5)

    with hf1:
        h_comm_type = st.selectbox(
            "📌 Type",
            options=['All Types'] + COMM_TYPES,
            key="h_comm_type"
        )
    with hf2:
        h_status = st.selectbox(
            "✅ Status",
            options=['All', 'sent', 'failed', 'pending'],
            key="h_status"
        )
    with hf3:
        h_limit = st.selectbox(
            "📊 Show",
            options=[25, 50, 100, 200],
            index=1,
            key="h_limit"
        )
    with hf4:
        st.markdown("<br/>", unsafe_allow_html=True)
        h_refresh = st.button(
            "🔄 Refresh",
            width='stretch',
            key="h_refresh"
        )
    with hf5:
        st.markdown("<br/>", unsafe_allow_html=True)
        h_student_filter = st.text_input(
            "🔍 Search Student",
            placeholder="Name or ID...",
            key="h_search"
        )

    st.markdown("---")

    # ── Build params ───────────────────────────────────────
    h_params = {"limit": h_limit}
    if h_comm_type != 'All Types':
        h_params['comm_type'] = h_comm_type
    if h_status != 'All':
        h_params['status'] = h_status

    # ── Fetch history ──────────────────────────────────────
    with st.spinner("Loading communication history..."):
        history_result = api_get("/communications/history", params=h_params)

    if history_result.get('status') != 'success':
        st.error(
            f"❌ {history_result.get('message', 'Could not load history')}"
        )
    else:
        history_data = history_result.get('data', {})
        history      = history_data.get('history', [])
        total        = history_data.get('total', 0)

        # ── Summary metrics ────────────────────────────────
        hm1, hm2, hm3, hm4 = st.columns(4)
        hm1.metric("📧 Total Showing",  len(history))
        hm2.metric("📊 Total Matching", total)
        hm3.metric(
            "✅ Sent",
            sum(1 for h in history if h.get('status') == 'sent')
        )
        hm4.metric(
            "❌ Failed",
            sum(1 for h in history if h.get('status') == 'failed')
        )

        st.markdown("---")

        if not history:
            st.info(
                "ℹ️ No communication records found. "
                "Send emails from the **Send Email** tab."
            )
        else:
            # ── Apply client-side search ───────────────────
            filtered = history
            if h_student_filter.strip():
                search = h_student_filter.strip().lower()
                filtered = [
                    h for h in history
                    if search in h.get('student_name', '').lower()
                    or search in str(h.get('student_code', '')).lower()
                ]

            if not filtered:
                st.warning(
                    f"⚠️ No records match '{h_student_filter}'"
                )
            else:
                # ── History table ──────────────────────────
                table_rows = []
                for h in filtered:
                    # Format sent_at
                    sent_at = h.get('sent_at', '')
                    if sent_at:
                        try:
                            sent_at = datetime.fromisoformat(
                                sent_at
                            ).strftime('%d %b %Y %I:%M %p')
                        except Exception:
                            pass

                    status_icon = (
                        '✅ Sent' if h.get('status') == 'sent'
                        else '❌ Failed' if h.get('status') == 'failed'
                        else '⏳ Pending'
                    )
                    comm_icon = COMM_TYPE_ICONS.get(
                        h.get('communication_type', ''), '📧'
                    )

                    table_rows.append({
                        'Student':  h.get('student_name'),
                        'ID':       h.get('student_code'),
                        'Grade':    f"{h.get('grade')}{h.get('section','')}",
                        'Type':     f"{comm_icon} {h.get('communication_type')}",
                        'To':       h.get('parent_email'),
                        'Status':   status_icon,
                        'Sent At':  sent_at,
                        'Subject':  h.get('subject', '')[:50] + '...'
                                    if len(h.get('subject', '')) > 50
                                    else h.get('subject', '')
                    })

                history_df = pd.DataFrame(table_rows)

                def style_status(val):
                    if '✅' in str(val):
                        return 'color:#00CC44; font-weight:700;'
                    elif '❌' in str(val):
                        return 'color:#FF4B4B; font-weight:700;'
                    else:
                        return 'color:#FFA500; font-weight:600;'

                styled_hist = history_df.style.map(
                    style_status, subset=['Status']
                )
                st.dataframe(
                    styled_hist,
                    width='stretch',
                    hide_index=True
                )

                # ── Expandable detail view ─────────────────
                st.markdown("---")
                st.markdown("#### 🔍 Detailed View")
                st.caption(
                    "Click any record below to view full email body"
                )

                for idx, h in enumerate(filtered[:20]):
                    sent_at_fmt = h.get('sent_at', '')
                    try:
                        sent_at_fmt = datetime.fromisoformat(
                            sent_at_fmt
                        ).strftime('%d %b %Y %I:%M %p')
                    except Exception:
                        pass

                    status_icon = (
                        '✅' if h.get('status') == 'sent'
                        else '❌'
                    )
                    comm_icon = COMM_TYPE_ICONS.get(
                        h.get('communication_type', ''), '📧'
                    )

                    with st.expander(
                        f"{status_icon} {comm_icon} "
                        f"{h.get('communication_type')}  |  "
                        f"{h.get('student_name')}  |  "
                        f"📧 {h.get('parent_email')}  |  "
                        f"🕐 {sent_at_fmt}",
                        expanded=False
                    ):
                        dc1, dc2 = st.columns(2)
                        with dc1:
                            st.markdown(
                                f"**👤 Student:** "
                                f"{h.get('student_name')}"
                            )
                            st.markdown(
                                f"**🆔 ID:** {h.get('student_code')}"
                            )
                            st.markdown(
                                f"**🎓 Grade:** "
                                f"{h.get('grade')}"
                                f"{h.get('section', '')}"
                            )
                            st.markdown(
                                f"**📌 Type:** "
                                f"{h.get('communication_type')}"
                            )
                        with dc2:
                            st.markdown(
                                f"**📧 Sent To:** "
                                f"{h.get('parent_email')}"
                            )
                            st.markdown(
                                f"**✅ Status:** "
                                f"{h.get('status', '').upper()}"
                            )
                            st.markdown(
                                f"**🕐 Sent At:** {sent_at_fmt}"
                            )
                            if h.get('error_message'):
                                st.markdown(
                                    f"**❌ Error:** "
                                    f"{h.get('error_message')}"
                                )

                        st.markdown(
                            f"**📋 Subject:** {h.get('subject')}"
                        )
                        st.markdown("**📝 Email Body:**")
                        st.markdown(
                            f'<div class="email-preview">'
                            f'{h.get("message_body", "—")}'
                            f'</div>',
                            unsafe_allow_html=True
                        )

                # ── Export ─────────────────────────────────
                st.markdown("---")
                export_df  = pd.DataFrame([{
                    'Student':   h.get('student_name'),
                    'ID':        h.get('student_code'),
                    'Grade':     f"{h.get('grade')}{h.get('section','')}",
                    'Type':      h.get('communication_type'),
                    'To':        h.get('parent_email'),
                    'Subject':   h.get('subject'),
                    'Status':    h.get('status'),
                    'Sent At':   h.get('sent_at'),
                    'Error':     h.get('error_message', '')
                } for h in filtered])

                csv = export_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Export History as CSV",
                    data=csv,
                    file_name=(
                        f"comm_history_"
                        f"{datetime.now().strftime('%Y%m%d')}.csv"
                    ),
                    mime="text/csv",
                    width='stretch'
                )


# ============================================================
# TAB 3 — TEMPLATES
# ============================================================
with tab3:
    st.markdown("### 📄 Email Templates")
    st.markdown(
        "All 7 built-in email templates used by ScholarSense. "
        "These are auto-filled with student data when sending."
    )
    st.markdown("---")

    # ── Fetch templates ────────────────────────────────────
    with st.spinner("Loading templates..."):
        templates_result = api_get("/communications/templates")

    if templates_result.get('status') != 'success':
        st.error("❌ Could not load templates.")
    else:
        templates = templates_result['data'].get('templates', [])

        # ── Template cards ─────────────────────────────────
        for tmpl in templates:
            icon = COMM_TYPE_ICONS.get(tmpl['name'], '📧')
            with st.expander(
                f"{icon} {tmpl['name']}",
                expanded=False
            ):
                tc1, tc2 = st.columns([1, 2])

                with tc1:
                    st.markdown(
                        f"**📌 Template Name:** {tmpl['name']}"
                    )
                    st.markdown(
                        f"**📋 Subject Line:**"
                    )
                    st.code(tmpl['subject'], language=None)

                    # Variable placeholders used
                    placeholders = {
                        'Risk Alert':        [
                            '{student_name}', '{risk_label}',
                            '{gpa}', '{failed_subjects}'
                        ],
                        'Academic Warning':  [
                            '{student_name}', '{gpa}',
                            '{failed_subjects}', '{semester}'
                        ],
                        'Behavioral Notice': [
                            '{student_name}', '{grade}',
                            '{section}'
                        ],
                        'Attendance Alert':  [
                            '{student_name}', '{parent_name}'
                        ],
                        'Marks Report':      [
                            '{student_name}', '{gpa}',
                            '{total_marks}', '{semester}'
                        ],
                        'General Update':    [
                            '{student_name}', '{custom_message}'
                        ],
                        'Custom':            [
                            '{custom_subject}', '{custom_message}'
                        ]
                    }
                    vars_used = placeholders.get(tmpl['name'], [])
                    if vars_used:
                        st.markdown("**🔧 Variables Used:**")
                        for v in vars_used:
                            st.markdown(
                                f"<span style='background:#edf2f7; "
                                f"padding:2px 8px; border-radius:6px; "
                                f"font-family:monospace; "
                                f"font-size:0.82rem;'>{v}</span>",
                                unsafe_allow_html=True
                            )

                with tc2:
                    st.markdown("**📝 Template Body Preview:**")
                    st.markdown(
                        f'<div class="email-preview">'
                        f'{tmpl["preview"]}'
                        f'</div>',
                        unsafe_allow_html=True
                    )

        st.markdown("---")

        # ── Template Usage Stats ───────────────────────────
        st.markdown(
            '<p class="section-header">📊 Template Usage</p>',
            unsafe_allow_html=True
        )

        if stats_res.get('status') == 'success':
            by_type = stats_res['data'].get('by_type', [])

            if by_type:
                type_labels = [x['type']  for x in by_type]
                type_values = [x['count'] for x in by_type]
                type_colors = [
                    '#2563eb', '#00CC44', '#FFA500',
                    '#FF4B4B', '#9467bd', '#8c564b', '#e377c2'
                ]

                fig_usage = go.Figure(data=[go.Bar(
                    x=type_labels,
                    y=type_values,
                    marker_color=type_colors[:len(type_labels)],
                    text=type_values,
                    textposition='outside',
                    width=0.5,
                    hovertemplate=(
                        '<b>%{x}</b><br>'
                        'Times Used: %{y}<extra></extra>'
                    )
                )])
                fig_usage.update_layout(
                    **get_plotly_layout(height=320, margin=dict(t=50, b=60, l=50, r=20),
                                       title="📧 Emails Sent per Template Type",
                                       xaxis=dict(title='Template', showgrid=False, tickangle=-20),
                                       yaxis=dict(title='Count', showgrid=True, gridcolor='#f0f0f0', rangemode='tozero'))
                )
                st.plotly_chart(fig_usage, width='stretch')
            else:
                st.info(
                    "ℹ️ No emails sent yet. "
                    "Usage stats will appear here after sending."
                )

        st.markdown("---")

        # ── Footer note ────────────────────────────────────
        st.markdown("""
        <div style='background:#f0f7ff; padding:1rem 1.5rem;
                    border-radius:10px; border-left:5px solid #2563eb;'>
            <b>💡 How Templates Work</b><br/>
            <ul style='margin:0.5rem 0 0 0; color:#4a5568;
                       font-size:0.9rem;'>
                <li>Variables like <code>{student_name}</code> are
                    automatically filled with real student data when
                    sending</li>
                <li>Templates are sent as both
                    <b>plain text</b> and <b>HTML email</b></li>
                <li>All emails include the ScholarSense header
                    and footer automatically</li>
                <li>For fully custom content, use the
                    <b>Custom</b> template type</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

