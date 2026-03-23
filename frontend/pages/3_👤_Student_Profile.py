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
import requests
from frontend.utils.session_manager import SessionManager
from frontend.utils.api_client import APIClient
import plotly.graph_objects as go
from datetime import datetime, date, timedelta

# ============================================
# PAGE CONFIG
# ============================================
st.set_page_config(
    page_title="Student Profile - ScholarSense",
    page_icon="👤",
    layout="wide"
)


from frontend.utils.sidebar import render_sidebar
render_sidebar()

from frontend.utils.ui_helpers import inject_theme_css
from frontend.utils.ui_helpers import get_plotly_layout
inject_theme_css()


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
    .incident-card { background: white; padding: 1rem 1.5rem; border-radius: 10px;
                     border: 1px solid #e2e8f0; margin-bottom: 0.75rem;
                     box-shadow: 0 1px 4px rgba(0,0,0,0.05); }
</style>
""", unsafe_allow_html=True)

# ============================================
# CONSTANTS (Enhancement 4)
# ============================================
API_BASE = "http://localhost:5000/api"

SEVERITY_COLORS = {
    'Minor':    '#00CC44',
    'Moderate': '#FFA500',
    'Serious':  '#FF4B4B',
    'Critical': '#8B0000'
}

SEVERITY_ICONS = {
    'Minor':    '🟢',
    'Moderate': '🟠',
    'Serious':  '🔴',
    'Critical': '🚨'
}

SEVERITY_LEVELS  = ['Minor', 'Moderate', 'Serious', 'Critical']
INCIDENT_TYPES   = [
    'Disciplinary', 'Disruptive', 'Bullying',
    'Academic Misconduct', 'Attendance Issue',
    'Property Damage', 'Other'
]

# ============================================
# API HELPERS (Enhancement 4)
# ============================================
def get_auth_headers():
    token = st.session_state.get('token', '')
    return {"Authorization": f"Bearer {token}"}

def fetch_student_incidents(student_id, limit=20):
    """Fetch incidents for a student"""
    try:
        r = requests.get(
            f"{API_BASE}/students/{student_id}/incidents",
            headers=get_auth_headers(),
            params={"limit": limit},
            timeout=10
        )
        return r.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}

def update_incident_api(incident_id, payload):
    """Update an incident"""
    try:
        r = requests.put(
            f"{API_BASE}/incidents/{incident_id}",
            headers=get_auth_headers(),
            json=payload,
            timeout=10
        )
        return r.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ============================================
# GET STUDENT ID
# ============================================
student_id = st.session_state.get('selected_student_id')
if not student_id:
    st.warning("⚠️ No student selected")
    if st.button("← Back to Students"):
        st.switch_page("pages/2_👥_Students.py")
    st.stop()



# ============================================
# FETCH STUDENT DETAILS
# ============================================
with st.spinner("Loading student details..."):
    details = APIClient.get_student_details(student_id)

if 'error' in details:
    st.error(f"❌ {details['error']}")
    st.stop()

# ============================================
# PAGE HEADER
# ============================================
col1, col2, col3 = st.columns([3, 1, 1])
with col1:
    st.title(f"👤 {details['first_name']} {details['last_name']}")
    st.markdown(
        f"**Student ID:** {details['student_id']} • "
        f"**Grade:** {details['grade']}-{details['section']}"
    )
with col2:
    if st.button("← Back to Students", use_container_width=True):
        st.switch_page("pages/2_👥_Students.py")
with col3:
    from frontend.utils.report_generator import generate_student_report
    from frontend.utils.activity_log import log_activity
    report_html = generate_student_report(details)
    st.download_button(
        label="📄 Export Report",
        data=report_html,
        file_name=f"report_{details['student_id']}.html",
        mime="text/html",
        use_container_width=True
    )
    # log only when button clicked — Streamlit handles this automatically

# ============================================
# TABS  ← Enhancement 4 adds "📝 Incidents"
# ============================================
tab1, tab2, tab3, tab4 = st.tabs([
    "📋 Overview",
    "📚 Academics",
    "🎯 Risk Assessment",
    "📝 Incidents"          # ← NEW
])


# ============================================================
# TAB 1 — OVERVIEW
# ============================================================
with tab1:
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

    # Parent contact info
    st.markdown('<p class="section-header">👨‍👩‍👦 Parent / Guardian</p>', unsafe_allow_html=True)
    pc1, pc2, pc3 = st.columns(3)
    with pc1:
        st.markdown(f"""
        <div class="info-box">
            <p class="info-label">Parent Name</p>
            <p class="info-value">{details.get('parent_name', 'N/A')}</p>
        </div>
        """, unsafe_allow_html=True)
    with pc2:
        st.markdown(f"""
        <div class="info-box">
            <p class="info-label">Phone</p>
            <p class="info-value">{details.get('parent_phone', 'N/A')}</p>
        </div>
        """, unsafe_allow_html=True)
    with pc3:
        st.markdown(f"""
        <div class="info-box">
            <p class="info-label">Email</p>
            <p class="info-value">{details.get('parent_email', 'N/A')}</p>
        </div>
        """, unsafe_allow_html=True)

    # Action buttons
    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🎯 Make New Prediction", type="primary", use_container_width=True):
            with st.spinner("Making prediction..."):
                result = APIClient.make_prediction(student_id)
                if 'error' not in result:
                    from frontend.utils.activity_log import log_activity
                    log_activity(
                        action="Prediction Run",
                        entity=f"{details['first_name']} {details['last_name']} → {result['risk_label']}",
                        icon="🎯",
                        level="info"
                    )
                    st.success(f"✅ Prediction updated: {result['risk_label']}")
                    st.rerun()
                else:
                    st.error(f"❌ {result['error']}")

    with col2:
        if st.button("📝 Add Academic Record", use_container_width=True):
            st.session_state['show_academic_form'] = True

    with col3:
        if st.button("🚨 Log Incident", use_container_width=True):
            st.switch_page("pages/6_📝_Incident_Logging.py")
    # ── Academic Record Form ──────────────────────────────────
    if st.session_state.get('show_academic_form'):
        st.markdown("---")
        st.markdown("### 📝 Add Academic Record")

        with st.form("academic_record_form"):
            r1, r2 = st.columns(2)
            with r1:
                semester = st.selectbox(
                    "Semester *",
                    ["Semester 1 - 2025", "Semester 2 - 2025",
                     "Semester 1 - 2026", "Semester 2 - 2026"]
                )
                current_gpa = st.number_input(
                    "Current GPA (%) *", min_value=0.0,
                    max_value=100.0, value=60.0, step=0.5
                )
                previous_gpa = st.number_input(
                    "Previous GPA (%)", min_value=0.0,
                    max_value=100.0, value=60.0, step=0.5
                )
                failed_subjects = st.number_input(
                    "Failed Subjects", min_value=0,
                    max_value=10, value=0
                )
                assignment_rate = st.number_input(
                    "Assignment Submission Rate (%)",
                    min_value=0.0, max_value=100.0,
                    value=80.0, step=1.0
                )
            with r2:
                math_score     = st.number_input("Math Score (%)",     0.0, 100.0, 60.0, 0.5)
                science_score  = st.number_input("Science Score (%)",  0.0, 100.0, 60.0, 0.5)
                english_score  = st.number_input("English Score (%)",  0.0, 100.0, 60.0, 0.5)
                social_score   = st.number_input("Social Score (%)",   0.0, 100.0, 60.0, 0.5)
                language_score = st.number_input("Language Score (%)", 0.0, 100.0, 60.0, 0.5)

            fc1, fc2 = st.columns(2)
            with fc1:
                submit = st.form_submit_button(
                    "💾 Save Academic Record",
                    type="primary",
                    use_container_width=True
                )
            with fc2:
                cancel = st.form_submit_button(
                    "✖ Cancel",
                    use_container_width=True
                )

        if cancel:
            st.session_state['show_academic_form'] = False
            st.rerun()

        if submit:
            payload = {
                "student_id":                  student_id,
                "semester":                    semester,
                "current_gpa":                 current_gpa,
                "previous_gpa":                previous_gpa,
                "grade_trend":                 round(current_gpa - previous_gpa, 2),
                "failed_subjects":             int(failed_subjects),
                "total_subjects":              5,
                "assignment_submission_rate":  assignment_rate,
                "math_score":                  math_score,
                "science_score":               science_score,
                "english_score":               english_score,
                "social_score":                social_score,
                "language_score":              language_score,
            }
            try:
                # ✅ REPLACE WITH:
                payload['student_id'] = student_id   # make sure student_id is in body

                resp = requests.post(
                    f"{API_BASE}/academics",          # ← correct route
                    headers=get_auth_headers(),
                    json=payload,
                    timeout=10
                )

                # ✅ REPLACE WITH:
                payload['student_id'] = student_id  # ensure student_id is in body

                resp = requests.post(
                    f"{API_BASE}/academics",        # ← fixed URL
                    headers=get_auth_headers(),
                    json=payload,
                    timeout=10
                )

                if resp.status_code == 201:
                    st.success("✅ Academic record saved!")
                    st.session_state['show_academic_form'] = False
                    st.rerun()
                else:
                    try:
                        result = resp.json()
                        st.error(f"❌ {result.get('error', 'Failed to save')}")
                    except:
                        st.error(f"❌ Server error: {resp.status_code}")

            except Exception as e:
                st.error(f"❌ Connection error: {e}")


    # ── Danger Zone ───────────────────────────────────────────
    st.markdown("---")
    st.markdown("**🚨 Danger Zone**")
    from frontend.utils.ui_helpers import confirm_dialog, show_toast

    student_name = f"{details['first_name']} {details['last_name']}"
    if confirm_dialog(
        "Delete Student",
        key=f"del_{student_id}",
        warning_msg=f"This will permanently delete {student_name} and ALL their records (grades, incidents, predictions)."
    ):
        result = APIClient.delete_student(student_id)
        if 'error' not in result:
            st.session_state['toast_msg']  = f"{student_name} deleted successfully."
            st.session_state['toast_type'] = 'warning'
            st.switch_page("pages/2_👥_Students.py")
        else:
            show_toast(result['error'], type='error')


# ============================================================
# TAB 2 — ACADEMICS
# ============================================================
with tab2:
    st.markdown('<p class="section-header">📚 Academic Performance</p>', unsafe_allow_html=True)

    if details.get('academic_records'):
        latest = details['academic_records'][0]

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Current GPA",
                f"{latest['current_gpa']}%",
                delta=f"{latest.get('grade_trend', 0):+.1f}%"
            )
        with col2:
            st.metric("Failed Subjects", latest.get('failed_subjects', 0))
        with col3:
            st.metric("Assignment Rate", f"{latest.get('assignment_submission_rate', 0)}%")
        with col4:
            st.metric("Semester", latest.get('semester', 'N/A'))

        # Subject scores chart
        if latest.get('math_score'):
            subjects = ['Math', 'Science', 'English', 'Social', 'Language']
            scores   = [
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
                **get_plotly_layout("Subject-wise Performance", height=350),
                yaxis_title="Score (%)",
            )
            st.plotly_chart(fig, use_container_width=True)

        # All academic records history
        if len(details['academic_records']) > 1:
            st.markdown("#### 📜 Academic History")
            import pandas as pd
            history_df = pd.DataFrame([
                {
                    'Semester': r.get('semester'),
                    'GPA': r.get('current_gpa'),
                    'Failed Subjects': r.get('failed_subjects'),
                    'Assignment Rate': r.get('assignment_submission_rate')
                }
                for r in details['academic_records']
            ])
            st.dataframe(history_df, use_container_width=True)
    else:
        st.info("📭 No academic records found")
        if st.button("➕ Add Academic Record", type="primary"):
            st.session_state['show_academic_form'] = True


# ============================================================
# TAB 3 — RISK ASSESSMENT
# ============================================================
with tab3:
    st.markdown('<p class="section-header">🎯 Risk Assessment</p>', unsafe_allow_html=True)

    if details.get('latest_risk_prediction'):
        pred       = details['latest_risk_prediction']
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
                <p class=\"info-value\">{float(pred.get('confidence_score') or 0):.1f}% Confidence</p>
            </div>
            """, unsafe_allow_html=True)

        # ✅ REPLACE WITH:
        with col2:
            categories = ['Low', 'Medium', 'High', 'Critical']
            probs      = [
                float(pred.get('probability_low')      or 0),
                float(pred.get('probability_medium')   or 0),
                float(pred.get('probability_high')     or 0),
                float(pred.get('probability_critical') or 0)
            ]
            colors = ['#10b981', '#f59e0b', '#ef4444', '#b91c1c']

            fig = go.Figure(data=[go.Bar(
                x=categories,
                y=probs,
                marker_color=colors,
                text=[f"{p:.1f}%" for p in probs],   # ✅ safe now

                textposition='outside'
            )])
            fig.update_layout(
                **get_plotly_layout("Risk Probability Distribution", height=300),
                yaxis_title="Probability (%)",
            )
            st.plotly_chart(fig, use_container_width=True)

        # Re-predict button
        st.markdown("---")
        if st.button("🔄 Re-run Prediction", type="primary"):
            with st.spinner("Running prediction..."):
                result = APIClient.make_prediction(student_id)
                if 'error' not in result:
                    from frontend.utils.activity_log import log_activity
                    log_activity(
                        action="Prediction Run",
                        entity=f"{details['first_name']} {details['last_name']} → {result['risk_label']}",
                        icon="🎯",
                        level="info"
                    )
                    st.success(f"✅ Updated: {result['risk_label']} ({result['confidence_score']:.1f}%)")
                    st.rerun()
                else:
                    st.error(f"❌ {result['error']}")

    else:
        st.info("📭 No risk prediction available")
        if st.button("🎯 Run First Prediction", type="primary"):
            with st.spinner("Making prediction..."):
                result = APIClient.make_prediction(student_id)
                if 'error' not in result:
                    st.success(f"✅ Prediction: {result['risk_label']}")
                    st.rerun()
                else:
                    st.error(f"❌ {result['error']}")


# ============================================================
# TAB 4 — INCIDENTS  ← Enhancement 4 (NEW)
# ============================================================
with tab4:
    st.markdown('<p class="section-header">📝 Behavioral Incident History</p>', unsafe_allow_html=True)

    # Controls row
    ctrl1, ctrl2, ctrl3 = st.columns([1, 1, 2])
    with ctrl1:
        incident_limit = st.selectbox(
            "Show Records",
            options=[10, 20, 50, 100],
            index=1
        )
    with ctrl2:
        st.markdown("<br/>", unsafe_allow_html=True)
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
    with ctrl3:
        st.markdown("<br/>", unsafe_allow_html=True)
        if st.button("🚨 Log New Incident for This Student",
                     use_container_width=True, type="primary"):
            # Pre-select student and redirect
            st.switch_page("pages/6_📝_Incident_Logging.py")

    st.markdown("---")

    # Fetch incidents
    with st.spinner("Loading incident history..."):
        incident_result = fetch_student_incidents(student_id, limit=incident_limit)

    if incident_result.get("status") != "success":
        st.error(f"❌ Could not load incidents: {incident_result.get('message', 'Unknown error')}")
    else:
        incident_data  = incident_result.get("data", {})
        incidents      = incident_data.get("incidents", [])
        total_incidents = incident_data.get("total", 0)

        # Summary metrics
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("📋 Total Incidents",   total_incidents)
        m2.metric("🚨 Critical",          sum(1 for i in incidents if i.get('severity') == 'Critical'))
        m3.metric("📞 Parent Notified",   sum(1 for i in incidents if i.get('parent_notified')))
        m4.metric("🧠 Counseling Given",  sum(1 for i in incidents if i.get('counseling_given')))

        st.markdown("---")

        if not incidents:
            st.success("✅ No behavioral incidents on record for this student.")
        else:
            # Severity distribution mini chart
            if len(incidents) >= 3:
                import pandas as pd
                sev_counts = pd.Series(
                    [i.get('severity') for i in incidents]
                ).value_counts()

                fig_sev = go.Figure(data=[go.Pie(
                    labels=sev_counts.index.tolist(),
                    values=sev_counts.values.tolist(),
                    marker_colors=[
                        SEVERITY_COLORS.get(s, '#ccc') for s in sev_counts.index
                    ],
                    hole=0.4
                )])
                fig_sev.update_layout(
                    **get_plotly_layout("Incidents by Severity", height=250),
                    margin=dict(t=40, b=10, l=10, r=10),
                )
                st.plotly_chart(fig_sev, use_container_width=True)
                st.markdown("---")

            # Incident cards
            for incident in incidents:
                severity     = incident.get('severity', 'Minor')
                icon         = SEVERITY_ICONS.get(severity, '📝')
                border_color = SEVERITY_COLORS.get(severity, '#ccc')

                with st.expander(
                    f"{icon} {severity}  |  "
                    f"{incident.get('incident_type')}  |  "
                    f"📅 {incident.get('incident_date')}",
                    expanded=False
                ):
                    c1, c2 = st.columns(2)

                    with c1:
                        st.markdown(f"**🔖 Incident ID:** #{incident.get('id')}")
                        st.markdown(f"**📌 Type:** {incident.get('incident_type')}")
                        st.markdown(f"**⚠️ Severity:** {incident.get('severity')}")
                        st.markdown(f"**📅 Date:** {incident.get('incident_date')}")
                        st.markdown(f"**🕐 Time:** {incident.get('incident_time') or '—'}")

                    with c2:
                        st.markdown(f"**📍 Location:** {incident.get('location') or '—'}")
                        st.markdown(f"**✅ Action Taken:** {incident.get('action_taken') or '—'}")
                        st.markdown(f"**📞 Parent Notified:** {'✅ Yes' if incident.get('parent_notified') else '❌ No'}")
                        st.markdown(f"**🧠 Counseling:** {'✅ Yes' if incident.get('counseling_given') else '❌ No'}")
                        st.markdown(f"**📆 Follow-up Date:** {incident.get('follow_up_date') or '—'}")

                    st.markdown("**📝 Description:**")
                    st.info(incident.get('description') or '—')

                    if incident.get('notes'):
                        st.markdown("**🗒️ Notes:**")
                        st.write(incident.get('notes'))

                    # ── Inline edit ────────────────────────────
                    st.markdown("---")
                    with st.expander("✏️ Update this Incident"):
                        with st.form(f"edit_incident_{incident['id']}"):
                            e1, e2 = st.columns(2)
                            with e1:
                                new_severity = st.selectbox(
                                    "Severity",
                                    options=SEVERITY_LEVELS,
                                    index=SEVERITY_LEVELS.index(severity)
                                    if severity in SEVERITY_LEVELS else 0
                                )
                                new_parent = st.checkbox(
                                    "Parent Notified",
                                    value=incident.get('parent_notified', False)
                                )
                            with e2:
                                new_counseling = st.checkbox(
                                    "Counseling Given",
                                    value=incident.get('counseling_given', False)
                                )
                                new_followup = st.date_input(
                                    "Follow-up Date",
                                    value=date.today() + timedelta(days=7)
                                )
                            new_action = st.text_area(
                                "Action Taken",
                                value=incident.get('action_taken') or ''
                            )
                            new_notes = st.text_area(
                                "Notes",
                                value=incident.get('notes') or ''
                            )

                            save_btn = st.form_submit_button(
                                "💾 Save Changes",
                                type="primary",
                                use_container_width=True
                            )

                        if save_btn:
                            upd_payload = {
                                "severity":         new_severity,
                                "parent_notified":  new_parent,
                                "counseling_given": new_counseling,
                                "follow_up_date":   new_followup.isoformat(),
                                "action_taken":     new_action,
                                "notes":            new_notes
                            }
                            upd_res = update_incident_api(incident['id'], upd_payload)
                            if upd_res.get('status') == 'success':
                                st.success("✅ Updated! Refresh to see changes.")
                            else:
                                st.error(f"❌ {upd_res.get('message', 'Update failed')}")
