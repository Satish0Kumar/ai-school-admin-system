"""
Parent Notification System
ScholarSense - Send Custom Academic Messages to Parents
"""
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from frontend.utils.session_manager import SessionManager

st.set_page_config(
    page_title="Parent Notifications - ScholarSense",
    page_icon="🔔",
    layout="wide"
)

from frontend.utils.sidebar import render_sidebar
render_sidebar()
from frontend.utils.ui_helpers import inject_theme_css
inject_theme_css()

SessionManager.require_auth()

st.markdown("""
<style>
    .main { background-color: #f7fafc; padding: 1rem 2rem; }
    .kpi-card { background: white; padding: 1.2rem 1rem; border-radius: 14px;
                border: 1px solid #e2e8f0; text-align: center; margin-bottom: 1rem; }
    .kpi-value { font-size: 2rem; font-weight: 800; margin: 0.2rem 0; }
    .kpi-label { font-size: 0.8rem; color: #4a5568; font-weight: 600;
                 text-transform: uppercase; letter-spacing: 0.04em; }
    .preview-box { background: #f8faff; padding: 1.5rem; border-radius: 10px;
                   border: 1px solid #c3dafe; font-family: Arial, sans-serif;
                   font-size: 0.9rem; line-height: 1.7; white-space: pre-wrap; color: #1a202c; }
    [data-testid="stSidebar"] { background-color: white; border-right: 1px solid #e2e8f0; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

API_BASE = "http://localhost:5000/api"
GRADES   = [6, 7, 8, 9, 10]

MESSAGE_TEMPLATES = {
    "📊 General Academic Update": (
        "Academic Update",
        "Dear {parent_name},\n\nThis is an academic update for your child {student_name} "
        "(Grade {grade}{section}).\n\n{custom_message}\n\nFor queries, please contact the school.\n\nWarm regards,\nScholarSense"
    ),
    "📉 Low GPA Alert": (
        "Academic Performance Alert",
        "Dear {parent_name},\n\nWe would like to inform you that {student_name}'s current GPA "
        "has dropped to {gpa}%, which is below our threshold of 50%.\n\n{custom_message}\n\n"
        "Please schedule a parent-teacher meeting at the earliest.\n\nWarm regards,\nScholarSense"
    ),
    "📅 Attendance Alert": (
        "Attendance Concern",
        "Dear {parent_name},\n\nWe are concerned about {student_name}'s attendance. "
        "Regular attendance is crucial for academic success.\n\n{custom_message}\n\n"
        "Warm regards,\nScholarSense"
    ),
    "🏆 Achievement Update": (
        "Achievement Notification",
        "Dear {parent_name},\n\nWe are pleased to share a positive update about {student_name}.\n\n"
        "{custom_message}\n\nKeep encouraging your child!\n\nWarm regards,\nScholarSense"
    ),
    "📝 Exam / Test Reminder": (
        "Upcoming Exam Reminder",
        "Dear {parent_name},\n\nThis is a reminder regarding an upcoming exam/test for {student_name}.\n\n"
        "{custom_message}\n\nPlease ensure your child is well-prepared.\n\nWarm regards,\nScholarSense"
    ),
    "✍️ Custom Message": (
        "Message from ScholarSense",
        "{custom_message}"
    ),
}

def get_headers():
    return {"Authorization": f"Bearer {st.session_state.get('token', '')}"}

def api_get(endpoint, params=None):
    try:
        r = requests.get(f"{API_BASE}{endpoint}", headers=get_headers(), params=params, timeout=15)
        return r.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}

def api_post(endpoint, payload):
    try:
        r = requests.post(f"{API_BASE}{endpoint}", headers=get_headers(), json=payload, timeout=30)
        return r.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_all_students():
    res = api_get("/students", params={"limit": 500})
    if isinstance(res, list):
        return res
    if isinstance(res, dict):
        return res.get('students', res.get('data', []))
    return []
def build_message(template_body, student, custom_message, gpa="N/A"):
    return template_body.format(
        parent_name    = student.get('parent_name', 'Parent/Guardian'),
        student_name   = f"{student.get('first_name','')} {student.get('last_name','')}",
        grade          = student.get('grade', ''),
        section        = student.get('section', ''),
        gpa            = gpa,
        custom_message = custom_message or ''
    )

# ── PAGE HEADER ─────────────────────────────────────────
st.markdown("""
    <h1 style='color:#1a202c; margin-bottom:0;'>🔔 Parent Notification System</h1>
    <p style='color:#4a5568; margin-top:0.25rem;'>
        Send custom academic messages to individual parents or entire grades/sections at once.
    </p>
    <hr style='border:none; border-top:1px solid #e2e8f0; margin:1rem 0;'/>
""", unsafe_allow_html=True)

# ── QUICK STATS ─────────────────────────────────────────
with st.spinner(""):
    stats_res = api_get("/communications/stats")

if stats_res.get('status') == 'success':
    stats = stats_res['data']
    qc1, qc2, qc3, qc4 = st.columns(4)
    sent_count   = next((x['count'] for x in stats.get('by_status', []) if x['status'] == 'sent'), 0)
    failed_count = next((x['count'] for x in stats.get('by_status', []) if x['status'] == 'failed'), 0)
    with qc1:
        st.markdown(f'<div class="kpi-card" style="border-top:4px solid #2563eb;"><p class="kpi-label">📧 Total Sent</p><p class="kpi-value" style="color:#2563eb;">{stats.get("total",0)}</p></div>', unsafe_allow_html=True)
    with qc2:
        st.markdown(f'<div class="kpi-card" style="border-top:4px solid #00CC44;"><p class="kpi-label">✅ Successful</p><p class="kpi-value" style="color:#00CC44;">{sent_count}</p></div>', unsafe_allow_html=True)
    with qc3:
        st.markdown(f'<div class="kpi-card" style="border-top:4px solid #FF4B4B;"><p class="kpi-label">❌ Failed</p><p class="kpi-value" style="color:#FF4B4B;">{failed_count}</p></div>', unsafe_allow_html=True)
    with qc4:
        st.markdown(f'<div class="kpi-card" style="border-top:4px solid #FFA500;"><p class="kpi-label">📅 Last 7 Days</p><p class="kpi-value" style="color:#FFA500;">{stats.get("last_week",0)}</p></div>', unsafe_allow_html=True)

st.markdown("---")

# ── SEND MODE ───────────────────────────────────────────
send_mode = st.radio(
    "📌 Select Send Mode",
    options=["👤 Single Student", "📚 Batch Send (Grade / Section)"],
    horizontal=True
)

st.markdown("---")

with st.spinner("Loading students..."):
    all_students = get_all_students()

if not all_students:
    st.warning("⚠️ No students found.")
    st.stop()

# ============================================================
# SINGLE STUDENT MODE
# ============================================================
if send_mode == "👤 Single Student":

    st.markdown("#### 👤 Step 1 — Select Student")
    student_map = {
        f"{s['student_id']} — {s['first_name']} {s['last_name']} "
        f"(Grade {s['grade']}{s.get('section','')})": s
        for s in all_students
    }
    sc1, sc2 = st.columns([3, 1])
    with sc1:
        sel_label = st.selectbox("Select Student", list(student_map.keys()), key="notif_single")
    sel_student  = student_map[sel_label]
    parent_email = sel_student.get('parent_email', '')
    with sc2:
        st.markdown("<br/>", unsafe_allow_html=True)
        if parent_email:
            st.success(f"📧 {parent_email}")
        else:
            st.error("❌ No parent email")

    st.markdown("---")
    st.markdown("#### 📋 Step 2 — Compose Message")

    mc1, mc2 = st.columns([2, 1])
    with mc1:
        sel_template = st.selectbox("📌 Message Type", list(MESSAGE_TEMPLATES.keys()), key="notif_tmpl")
    with mc2:
        if sel_template in ("📉 Low GPA Alert",):
            gpa_val = st.number_input("📊 GPA (%)", 0.0, 100.0, 50.0, 0.5, key="notif_gpa")
        else:
            gpa_val = "N/A"

    custom_msg = st.text_area(
        "✍️ Your Message / Additional Details *",
        placeholder="Write your message here. This will be inserted into the template...",
        height=120,
        key="notif_msg"
    )

    _, template_body = MESSAGE_TEMPLATES[sel_template]
    preview_text = build_message(template_body, sel_student, custom_msg, gpa_val)

    st.markdown("---")
    st.markdown("#### 👁️ Step 3 — Preview Email")
    with st.expander("📬 Preview Email", expanded=True):
        st.markdown(f'<div class="preview-box">{preview_text}</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### 📤 Step 4 — Send")

    if not parent_email:
        st.error("❌ No parent email on file. Update student record first.")
    elif not custom_msg.strip():
        st.warning("⚠️ Please write a message before sending.")
    else:
        if st.button(f"📤 Send to {parent_email}", type="primary", width='stretch', key="single_notif_send"):
            template_subject, _ = MESSAGE_TEMPLATES[sel_template]
            payload = {
                'student_id':          sel_student['id'],
                'communication_type':  'Custom',
                'custom_subject':      template_subject,
                'custom_message':      preview_text,
                'extra_data':          {}
            }
            with st.spinner("📤 Sending..."):
                result = api_post("/communications/send", payload)
            if result.get('status') == 'success':
                st.success(f"✅ Message sent to **{parent_email}**!")
                st.balloons()
            else:
                st.error(f"❌ Failed: {result.get('message', 'Unknown error')}")

# ============================================================
# BATCH SEND MODE
# ============================================================
else:
    st.markdown("#### 📚 Step 1 — Select Target Grade & Section")

    bc1, bc2 = st.columns(2)
    with bc1:
        sel_grade   = st.selectbox("🎓 Grade", ["All Grades"] + GRADES, key="notif_grade")
    with bc2:
        sel_section = st.selectbox("📌 Section", ["All Sections", "A", "B", "C", "D", "E"], key="notif_section")

    # Filter students
    filtered = [
        s for s in all_students
        if (sel_grade == "All Grades" or s.get('grade') == sel_grade) and
           (sel_section == "All Sections" or s.get('section') == sel_section)
    ]
    with_email = [s for s in filtered if s.get('parent_email')]
    no_email   = [s for s in filtered if not s.get('parent_email')]

    # Preview table
    if filtered:
        st.dataframe(pd.DataFrame([{
            'Student':      f"{s['first_name']} {s['last_name']}",
            'Grade':        f"{s['grade']}{s.get('section','')}",
            'Parent Email': s.get('parent_email') or '❌ No email'
        } for s in filtered]), width='stretch', hide_index=True)

        col1, col2 = st.columns(2)
        with col1:
            st.success(f"✅ **{len(with_email)}** students will receive the message")
        with col2:
            if no_email:
                st.warning(f"⚠️ **{len(no_email)}** skipped — no parent email")

    st.markdown("---")
    st.markdown("#### 📋 Step 2 — Compose Message")

    mc1, mc2 = st.columns([2, 1])
    with mc1:
        sel_template = st.selectbox("📌 Message Type", list(MESSAGE_TEMPLATES.keys()), key="batch_tmpl")

    custom_msg = st.text_area(
        "✍️ Your Message / Additional Details *",
        placeholder="Write your message here. It will be personalised for each student...",
        height=120,
        key="batch_msg"
    )

    # Preview with first student as sample
    if with_email:
        _, template_body  = MESSAGE_TEMPLATES[sel_template]
        sample_preview    = build_message(template_body, with_email[0], custom_msg)
        st.markdown("#### 👁️ Preview (sample — first student)")
        with st.expander("📬 Preview Email", expanded=False):
            st.markdown(f'<div class="preview-box">{sample_preview}</div>', unsafe_allow_html=True)
        st.caption("⚠️ Each email will be personalised with the student's name, grade, and parent name.")

    st.markdown("---")
    st.markdown("#### 📤 Step 3 — Send")

    if not filtered:
        st.warning("⚠️ No students in this selection.")
    elif len(with_email) == 0:
        st.error("❌ No students in this selection have parent emails.")
    elif not custom_msg.strip():
        st.warning("⚠️ Please write a message before sending.")
    else:
        st.warning(f"⚠️ This will send **{len(with_email)} emails**. This cannot be undone.")
        if st.button(
            f"🚀 Send to All {len(with_email)} Parents",
            type="primary", width='stretch', key="batch_notif_send"
        ):
            template_subject, template_body = MESSAGE_TEMPLATES[sel_template]
            progress     = st.progress(0, text="Starting...")
            success_count, fail_count = 0, 0
            results_log  = []

            for idx, student in enumerate(with_email):
                name = f"{student['first_name']} {student['last_name']}"
                progress.progress(
                    int((idx + 1) / len(with_email) * 100),
                    text=f"📤 Sending to {name}... ({idx+1}/{len(with_email)})"
                )
                personalized_msg = build_message(template_body, student, custom_msg)
                payload = {
                    'student_id':         student['id'],
                    'communication_type': 'Custom',
                    'custom_subject':     template_subject,
                    'custom_message':     personalized_msg,
                    'extra_data':         {}
                }
                result = api_post("/communications/send", payload)
                if result.get('status') == 'success':
                    success_count += 1
                    results_log.append({'Student': name, 'Email': student['parent_email'], 'Status': '✅ Sent'})
                else:
                    fail_count += 1
                    results_log.append({'Student': name, 'Email': student['parent_email'], 'Status': '❌ Failed'})

            progress.progress(100, text="✅ Done!")
            st.success(f"✅ Done! **{success_count}** sent | **{fail_count}** failed")
            if success_count > 0:
                st.balloons()

            st.dataframe(pd.DataFrame(results_log), width='stretch', hide_index=True)
