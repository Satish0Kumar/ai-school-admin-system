"""
Incident Logging Page
ScholarSense - AI-Powered Academic Intelligence System
Enhancement 4: Behavioral Incident Management
"""

import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta

# ============================================
# CONFIG
# ============================================
API_BASE = "http://localhost:5000/api"

INCIDENT_TYPES = [
    'Disciplinary',
    'Disruptive',
    'Bullying',
    'Late Arrival',
    'Absence',
    'Other'
]

SEVERITY_LEVELS = [
    'Minor',
    'Moderate',
    'Serious',
    'Critical'
]

SEVERITY_COLORS = {
    'Minor':    '#00CC44',
    'Moderate': '#FFA500',
    'Serious':  '#FF4B4B',
    'Critical': '#8B0000'
}

SEVERITY_BADGE = {
    'Minor':    '🟢 Minor',
    'Moderate': '🟠 Moderate',
    'Serious':  '🔴 Serious',
    'Critical': '🚨 Critical'
}

# ============================================
# SESSION CHECK
# ============================================
if 'token' not in st.session_state:
    st.error("🔒 Please login first")
    st.stop()

TOKEN   = st.session_state['token']
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

# ============================================
# HELPERS
# ============================================
def api_get(endpoint, params=None):
    try:
        r = requests.get(f"{API_BASE}{endpoint}", headers=HEADERS, params=params, timeout=10)
        return r.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}

def api_post(endpoint, payload):
    try:
        r = requests.post(f"{API_BASE}{endpoint}", headers=HEADERS, json=payload, timeout=10)
        return r.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}

def api_put(endpoint, payload):
    try:
        r = requests.put(f"{API_BASE}{endpoint}", headers=HEADERS, json=payload, timeout=10)
        return r.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_students_list():
    """Fetch all active students for dropdown"""
    res = api_get("/students")
    if isinstance(res, list):
        return res
    return []

def severity_badge(severity):
    return SEVERITY_BADGE.get(severity, severity)

def color_severity_row(severity):
    return SEVERITY_COLORS.get(severity, '#FFFFFF')

# ============================================
# PAGE HEADER
# ============================================
st.set_page_config(page_title="Incident Logging", page_icon="📝", layout="wide")

from frontend.utils.sidebar import render_sidebar
render_sidebar()


st.markdown("""
    <h1 style='color:#1f77b4;'>📝 Behavioral Incident Logging</h1>
    <p style='color:gray;'>Log, track and manage student behavioral incidents</p>
    <hr/>
""", unsafe_allow_html=True)

# ============================================
# TABS
# ============================================
tab1, tab2 = st.tabs(["➕ Log New Incident", "📋 View Incidents"])


# ============================================================
# TAB 1 — LOG NEW INCIDENT
# ============================================================
with tab1:
    st.markdown("### 📋 New Behavioral Incident Report")
    st.markdown("Fill in all required fields (marked with *) and submit.")
    st.markdown("---")

    # Load student list
    students = get_students_list()
    if not students:
        st.warning("⚠️ Could not load student list. Check API connection.")
        st.stop()

    student_options = {
        f"{s['student_id']} — {s['first_name']} {s['last_name']} (Grade {s['grade']}{s.get('section','')})": s['id']
        for s in students
    }

    with st.form("incident_form", clear_on_submit=True):

        # ── Row 1: Student + Date ──────────────────────────────
        col1, col2 = st.columns([2, 1])
        with col1:
            student_label = st.selectbox(
                "👤 Student *",
                options=list(student_options.keys()),
                help="Select the student involved in the incident"
            )
        with col2:
            incident_date = st.date_input(
                "📅 Incident Date *",
                value=date.today(),
                max_value=date.today()
            )

        # ── Row 2: Type + Severity + Time ─────────────────────
        col3, col4, col5 = st.columns(3)
        with col3:
            incident_type = st.selectbox(
                "📌 Incident Type *",
                options=INCIDENT_TYPES
            )
        with col4:
            severity = st.selectbox(
                "⚠️ Severity *",
                options=SEVERITY_LEVELS,
                help="Minor → Moderate → Serious → Critical"
            )
        with col5:
            incident_time = st.time_input(
                "🕐 Time of Incident",
                value=datetime.now().time()
            )

        # ── Row 3: Location ────────────────────────────────────
        location = st.text_input(
            "📍 Location",
            placeholder="e.g., Classroom 5A, Playground, Corridor..."
        )

        # ── Row 4: Description ─────────────────────────────────
        description = st.text_area(
            "📝 Description *",
            placeholder="Describe the incident in detail...",
            height=120
        )

        # ── Row 5: Action Taken ────────────────────────────────
        action_taken = st.text_area(
            "✅ Action Taken",
            placeholder="What action was taken immediately?",
            height=80
        )

        # ── Row 6: Witnesses ───────────────────────────────────
        witnesses = st.text_input(
            "👥 Witnesses",
            placeholder="Names of witnesses (if any)"
        )

        # ── Row 7: Checkboxes + Follow-up ─────────────────────
        col6, col7, col8 = st.columns(3)
        with col6:
            parent_notified = st.checkbox("📞 Parent Notified")
        with col7:
            counseling_given = st.checkbox("🧠 Counseling Given")
        with col8:
            follow_up_needed = st.checkbox("📆 Follow-up Required")

        follow_up_date = None
        if follow_up_needed:
            follow_up_date = st.date_input(
                "📆 Follow-up Date",
                value=date.today() + timedelta(days=7),
                min_value=date.today()
            )

        # ── Row 8: Notes ───────────────────────────────────────
        notes = st.text_area(
            "🗒️ Additional Notes",
            placeholder="Any additional notes or observations...",
            height=80
        )

        # ── Submit ─────────────────────────────────────────────
        st.markdown("---")
        submitted = st.form_submit_button(
            "🚨 Submit Incident Report",
            use_container_width=True,
            type="primary"
        )

    # Handle submission
    if submitted:
        # Validate required
        if not description.strip():
            st.error("❌ Description is required.")
        else:
            payload = {
                "student_id":       student_options[student_label],
                "incident_date":    incident_date.isoformat(),
                "incident_time":    incident_time.strftime('%H:%M:%S'),
                "incident_type":    incident_type,
                "severity":         severity,
                "description":      description.strip(),
                "location":         location.strip() or None,
                "action_taken":     action_taken.strip() or None,
                "witnesses":        witnesses.strip() or None,
                "parent_notified":  parent_notified,
                "counseling_given": counseling_given,
                "follow_up_date":   follow_up_date.isoformat() if follow_up_date else None,
                "notes":            notes.strip() or None
            }

            with st.spinner("📤 Submitting incident report..."):
                result = api_post("/incidents/log", payload)

            if result.get('status') == 'success':
                st.success("✅ Incident logged successfully!")

                # Show summary card
                inc = result['data']
                st.markdown(f"""
                <div style='background:#f0f2f6; padding:15px; border-radius:10px;
                            border-left: 5px solid {SEVERITY_COLORS.get(severity,"#ccc")};'>
                    <b>📋 Incident Summary</b><br/>
                    🔖 ID: <b>#{inc.get('id')}</b> &nbsp;|&nbsp;
                    📌 Type: <b>{inc.get('incident_type')}</b> &nbsp;|&nbsp;
                    ⚠️ Severity: <b>{inc.get('severity')}</b><br/>
                    📅 Date: <b>{inc.get('incident_date')}</b> &nbsp;|&nbsp;
                    📞 Parent Notified: <b>{'Yes' if inc.get('parent_notified') else 'No'}</b>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.error(f"❌ Failed: {result.get('message', 'Unknown error')}")


# ============================================================
# TAB 2 — VIEW INCIDENTS
# ============================================================
with tab2:
    st.markdown("### 📋 Behavioral Incidents Log")
    st.markdown("---")

    # ── Filters ────────────────────────────────────────────
    st.markdown("#### 🔍 Filters")
    fc1, fc2, fc3, fc4, fc5 = st.columns(5)

    with fc1:
        filter_date_from = st.date_input(
            "From Date",
            value=date.today() - timedelta(days=30)
        )
    with fc2:
        filter_date_to = st.date_input(
            "To Date",
            value=date.today()
        )
    with fc3:
        filter_severity = st.selectbox(
            "Severity",
            options=["All"] + SEVERITY_LEVELS
        )
    with fc4:
        filter_type = st.selectbox(
            "Incident Type",
            options=["All"] + INCIDENT_TYPES
        )
    with fc5:
        filter_limit = st.selectbox(
            "Show Records",
            options=[25, 50, 100],
            index=0
        )

    st.markdown("---")

    # ── Build query params ─────────────────────────────────
    params = {
        "date_from": filter_date_from.isoformat(),
        "date_to":   filter_date_to.isoformat(),
        "limit":     filter_limit
    }
    if filter_severity != "All":
        params["severity"] = filter_severity
    if filter_type != "All":
        params["type"] = filter_type

    # ── Fetch incidents ────────────────────────────────────
    with st.spinner("Loading incidents..."):
        result = api_get("/incidents", params=params)

    if result.get('status') != 'success':
        st.error(f"❌ Could not load incidents: {result.get('message')}")
    else:
        incidents = result['data'].get('incidents', [])
        total     = result['data'].get('total', 0)

        # Summary metric
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        col_m1.metric("📋 Total Shown", len(incidents))
        col_m2.metric("📊 Total Matching", total)
        critical_count = sum(1 for i in incidents if i.get('severity') == 'Critical')
        col_m3.metric("🚨 Critical", critical_count)
        notified_count = sum(1 for i in incidents if i.get('parent_notified'))
        col_m4.metric("📞 Parent Notified", notified_count)

        st.markdown("---")

        if not incidents:
            st.info("ℹ️ No incidents found for the selected filters.")
        else:
            # ── Display incidents as cards ─────────────────
            for inc in incidents:
                severity_val = inc.get('severity', 'Minor')
                border_color = SEVERITY_COLORS.get(severity_val, '#ccc')
                badge        = severity_badge(severity_val)

                with st.expander(
                    f"{badge} | #{inc.get('id')} | "
                    f"{inc.get('incident_type')} | "
                    f"Student ID: {inc.get('student_id')} | "
                    f"📅 {inc.get('incident_date')}",
                    expanded=False
                ):
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        st.markdown(f"**📌 Type:** {inc.get('incident_type')}")
                        st.markdown(f"**📍 Location:** {inc.get('location') or '—'}")
                        st.markdown(f"**🕐 Time:** {inc.get('incident_time') or '—'}")
                    with c2:
                        st.markdown(f"**📞 Parent Notified:** {'✅ Yes' if inc.get('parent_notified') else '❌ No'}")
                        st.markdown(f"**🧠 Counseling:** {'✅ Yes' if inc.get('counseling_given') else '❌ No'}")
                        st.markdown(f"**📆 Follow-up:** {inc.get('follow_up_date') or '—'}")
                    with c3:
                        st.markdown(f"**✅ Action Taken:** {inc.get('action_taken') or '—'}")

                    st.markdown(f"**📝 Description:**")
                    st.info(inc.get('description', '—'))

                    # ── Edit form ──────────────────────────
                    st.markdown("---")
                    with st.expander("✏️ Edit this Incident"):
                        with st.form(f"edit_form_{inc['id']}"):
                            e1, e2 = st.columns(2)
                            with e1:
                                new_severity = st.selectbox(
                                    "Severity",
                                    options=SEVERITY_LEVELS,
                                    index=SEVERITY_LEVELS.index(severity_val)
                                )
                                new_parent = st.checkbox(
                                    "Parent Notified",
                                    value=inc.get('parent_notified', False)
                                )
                            with e2:
                                new_counseling = st.checkbox(
                                    "Counseling Given",
                                    value=inc.get('counseling_given', False)
                                )
                                new_followup = st.date_input(
                                    "Follow-up Date",
                                    value=date.today() + timedelta(days=7)
                                )
                            new_action = st.text_area(
                                "Action Taken",
                                value=inc.get('action_taken') or ''
                            )
                            new_notes = st.text_area(
                                "Notes",
                                value=inc.get('notes') or ''
                            )
                            edit_submitted = st.form_submit_button(
                                "💾 Save Changes",
                                type="primary"
                            )

                        if edit_submitted:
                            update_payload = {
                                "severity":         new_severity,
                                "parent_notified":  new_parent,
                                "counseling_given": new_counseling,
                                "follow_up_date":   new_followup.isoformat(),
                                "action_taken":     new_action,
                                "notes":            new_notes
                            }
                            upd_result = api_put(
                                f"/incidents/{inc['id']}",
                                update_payload
                            )
                            if upd_result.get('status') == 'success':
                                st.success("✅ Incident updated! Refresh to see changes.")
                            else:
                                st.error(f"❌ {upd_result.get('message')}")
