"""
Parent Report Portal
ScholarSense - Send PDF Academic Reports via Email to Parents
"""
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import streamlit as st
import requests
import pandas as pd
from frontend.utils.session_manager import SessionManager

st.set_page_config(
    page_title="Send Reports - ScholarSense",
    page_icon="📎",
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
    [data-testid="stSidebar"] { background-color: white; border-right: 1px solid #e2e8f0; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

API_BASE = "http://localhost:5000/api"
GRADES   = [6, 7, 8, 9, 10]

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
# ── PAGE HEADER ─────────────────────────────────────────
st.markdown("""
    <h1 style='color:#1a202c; margin-bottom:0;'>📎 Send Academic Report to Parents</h1>
    <p style='color:#4a5568; margin-top:0.25rem;'>
        Generate PDF academic reports and email them directly to parents.
    </p>
    <hr style='border:none; border-top:1px solid #e2e8f0; margin:1rem 0;'/>
""", unsafe_allow_html=True)

# ── SEND MODE ───────────────────────────────────────────
report_mode = st.radio(
    "📌 Select Mode",
    options=["👤 Single Student", "📚 Batch by Grade & Section"],
    horizontal=True
)

st.markdown("---")

with st.spinner("Loading students..."):
    all_students = get_all_students()

if not all_students:
    st.warning("⚠️ No students found. Check API connection.")
    st.stop()

# ============================================================
# SINGLE STUDENT MODE
# ============================================================
if report_mode == "👤 Single Student":
    st.markdown("#### 👤 Select Student")

    student_map = {
        f"{s['student_id']} — {s['first_name']} {s['last_name']} "
        f"(Grade {s['grade']}{s.get('section', '')})": s
        for s in all_students
    }

    sc1, sc2 = st.columns([3, 1])
    with sc1:
        sel_label   = st.selectbox("Select Student", options=list(student_map.keys()), key="rpt_single")
    sel_student     = student_map[sel_label]
    parent_email    = sel_student.get('parent_email', '')

    with sc2:
        st.markdown("<br/>", unsafe_allow_html=True)
        if parent_email:
            st.success(f"📧 {parent_email}")
        else:
            st.error("❌ No parent email")

    st.markdown("---")

    if not parent_email:
        st.error("❌ Cannot send — update the student record with a parent email first.")
    else:
        st.info(
            f"📄 A PDF report will be generated for "
            f"**{sel_student['first_name']} {sel_student['last_name']}** "
            f"and emailed to **{parent_email}**"
        )
        if st.button("📨 Generate & Send Report", type="primary", width='stretch', key="single_send"):
            token = st.session_state.get('token', '')
            with st.spinner("⏳ Generating PDF report..."):
                pdf_res = requests.get(
                    f"{API_BASE}/reports/student/{sel_student['id']}",
                    headers=get_headers(), timeout=30
                )
            if pdf_res.status_code != 200:
                st.error("❌ PDF generation failed. Make sure `reportlab` is installed on the server.")
            else:
                with st.spinner("📤 Sending email with PDF attachment..."):
                    result = api_post("/communications/send-report", {
                        'student_id': sel_student['id'],
                        'communication_type': 'Marks Report',
                        'pdf_report': True
                    })
                if result.get('status') == 'success':
                    st.success(f"✅ PDF Report emailed successfully to **{parent_email}**!")
                    st.balloons()
                else:
                    st.warning("⚠️ Email failed — download the PDF manually below.")
                    st.download_button(
                        label="⬇️ Download PDF Manually",
                        data=pdf_res.content,
                        file_name=f"report_{sel_student['student_id']}.pdf",
                        mime="application/pdf"
                    )

# ============================================================
# BATCH MODE
# ============================================================
else:
    st.markdown("#### 📚 Select Grade & Section")

    bc1, bc2 = st.columns(2)
    with bc1:
        sel_grade   = st.selectbox("🎓 Grade", options=["All Grades"] + GRADES, key="rpt_grade")
    with bc2:
        sel_section = st.selectbox(
            "📌 Section",
            options=["All Sections", "A", "B", "C", "D", "E"],
            key="rpt_section"
        )

    # Filter students by grade + section
    filtered = [
        s for s in all_students
        if (sel_grade == "All Grades" or s.get('grade') == sel_grade) and
           (sel_section == "All Sections" or s.get('section') == sel_section)
    ]

    with_email = [s for s in filtered if s.get('parent_email')]
    no_email   = [s for s in filtered if not s.get('parent_email')]

    st.markdown("---")

    if not filtered:
        st.warning("⚠️ No students found for the selected filter.")
    else:
        # Preview table
        preview_rows = [{
            'Student':      f"{s['first_name']} {s['last_name']}",
            'ID':           s['student_id'],
            'Grade':        f"{s['grade']}{s.get('section', '')}",
            'Parent Email': s.get('parent_email') or '❌ No email'
        } for s in filtered]

        st.dataframe(pd.DataFrame(preview_rows), width='stretch', hide_index=True)

        c1, c2 = st.columns(2)
        with c1:
            st.success(f"✅ **{len(with_email)}** students have parent email — will receive report")
        with c2:
            if no_email:
                st.warning(f"⚠️ **{len(no_email)}** students have no email — will be skipped")

        st.markdown("---")

        if len(with_email) == 0:
            st.error("❌ No students in this selection have parent emails. Update student records first.")
        else:
            st.warning(
                f"⚠️ This will generate and email **{len(with_email)} PDF reports**. "
                f"This may take a few minutes."
            )
            if st.button(
                f"📨 Generate & Send {len(with_email)} PDF Reports",
                type="primary", width='stretch', key="batch_send"
            ):
                token    = st.session_state.get('token', '')
                progress = st.progress(0, text="Starting...")
                success_count, fail_count = 0, 0
                results_log = []

                for idx, student in enumerate(with_email):
                    name = f"{student['first_name']} {student['last_name']}"
                    progress.progress(
                        int((idx + 1) / len(with_email) * 100),
                        text=f"📤 Sending report for {name}... ({idx+1}/{len(with_email)})"
                    )
                    pdf_res = requests.get(
                        f"{API_BASE}/reports/student/{student['id']}",
                        headers=get_headers(), timeout=30
                    )
                    if pdf_res.status_code == 200:
                        result = api_post("/communications/send-report", {
                            'student_id': student['id'],
                            'communication_type': 'Marks Report',
                            'pdf_report': True
                        })
                        if result.get('status') == 'success':
                            success_count += 1
                            results_log.append({'Student': name, 'Email': student['parent_email'], 'Status': '✅ Sent'})
                        else:
                            fail_count += 1
                            results_log.append({'Student': name, 'Email': student['parent_email'], 'Status': '❌ Failed'})
                    else:
                        fail_count += 1
                        results_log.append({'Student': name, 'Email': student['parent_email'], 'Status': '❌ PDF Error'})

                progress.progress(100, text="✅ Done!")
                st.success(f"✅ Batch complete! **{success_count}** sent | **{fail_count}** failed")
                if success_count > 0:
                    st.balloons()

                # Results table
                st.dataframe(pd.DataFrame(results_log), width='stretch', hide_index=True)
