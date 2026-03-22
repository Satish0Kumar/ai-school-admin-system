"""
Notifications Page - Parent Alert System
ScholarSense - AI-Powered Academic Intelligence System

Features:
- Notification statistics dashboard
- Grade/Section wise bulk send
- Notification history table
- Per-student manual notify
"""

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import streamlit as st
import requests
from datetime import datetime
from frontend.utils.session_manager import SessionManager
from frontend.utils.api_client import APIClient

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title = "Notifications - ScholarSense",
    page_icon  = "🔔",
    layout     = "wide"
)

from frontend.utils.sidebar import render_sidebar
render_sidebar()

from frontend.utils.ui_helpers import inject_theme_css
inject_theme_css()


SessionManager.initialize_session()
SessionManager.require_auth()

token = SessionManager.get_token()

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .stat-card {
        background: white;
        border-radius: 14px;
        padding: 20px 24px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.07);
        text-align: center;
        border-top: 4px solid #2563eb;
    }
    .stat-card.green  { border-top-color: #10b981; }
    .stat-card.red    { border-top-color: #ef4444; }
    .stat-card.orange { border-top-color: #f59e0b; }
    .stat-card.purple { border-top-color: #8b5cf6; }

    .stat-number {
        font-size: 2.4rem;
        font-weight: 800;
        color: #1a202c;
        margin: 0;
        line-height: 1;
    }
    .stat-label {
        font-size: 0.88rem;
        color: #6b7280;
        margin-top: 6px;
        font-weight: 500;
    }

    .section-header {
        font-size: 1.2rem;
        font-weight: 700;
        color: #1a202c;
        margin: 1.5rem 0 1rem 0;
        padding-bottom: 8px;
        border-bottom: 2px solid #e5e7eb;
    }

    .notif-badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 600;
    }
    .badge-sent     { background:#d1fae5; color:#065f46; }
    .badge-failed   { background:#fee2e2; color:#991b1b; }
    .badge-pending  { background:#fef3c7; color:#92400e; }

    .type-badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 6px;
        font-size: 0.78rem;
        font-weight: 600;
    }
    .type-low_gpa         { background:#fef3c7; color:#92400e; }
    .type-high_risk       { background:#fee2e2; color:#991b1b; }
    .type-low_attendance  { background:#fff7ed; color:#9a3412; }
    .type-failed_subjects { background:#f5f3ff; color:#5b21b6; }

    .send-panel {
        background: white;
        border-radius: 14px;
        padding: 24px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.07);
        margin-bottom: 1rem;
    }

    #MainMenu { visibility: hidden; }
    footer    { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ── Helper: API calls ──────────────────────────────────────────────────────────
def api_get(endpoint):
    try:
        r = requests.get(
            f"http://localhost:5000{endpoint}",
            headers = {'Authorization': f'Bearer {token}'},
            timeout = 30
        )
        return r.json() if r.status_code == 200 else {}
    except Exception as e:
        return {}

def api_post(endpoint, body={}):
    try:
        r = requests.post(
            f"http://localhost:5000{endpoint}",
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type' : 'application/json'
            },
            json    = body,
            timeout = 300   # 5 min for bulk operations
        )
        return r.json()
    except Exception as e:
        return {'error': str(e)}


# ── Page Title ─────────────────────────────────────────────────────────────────
st.markdown("# 🔔 Parent Notification System")
st.markdown("Send automated alerts to parents based on student academic performance.")
st.markdown("---")


# ==============================================================================
# SECTION 1 — STATS CARDS
# ==============================================================================

stats = api_get('/api/notifications/stats')

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(f"""
    <div class="stat-card">
        <p class="stat-number">{stats.get('total', 0)}</p>
        <p class="stat-label">📊 Total Sent</p>
    </div>""", unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="stat-card green">
        <p class="stat-number">{stats.get('sent', 0)}</p>
        <p class="stat-label">✅ Successful</p>
    </div>""", unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="stat-card red">
        <p class="stat-number">{stats.get('failed', 0)}</p>
        <p class="stat-label">❌ Failed</p>
    </div>""", unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="stat-card orange">
        <p class="stat-number">{stats.get('today', 0)}</p>
        <p class="stat-label">📅 Today</p>
    </div>""", unsafe_allow_html=True)

with col5:
    by_type    = stats.get('by_type', {})
    high_risk  = by_type.get('high_risk', 0)
    st.markdown(f"""
    <div class="stat-card purple">
        <p class="stat-number">{high_risk}</p>
        <p class="stat-label">🚨 High Risk Alerts</p>
    </div>""", unsafe_allow_html=True)

st.write("")

# ── Type breakdown ─────────────────────────────────────────────────────────────
by_type = stats.get('by_type', {})
if any(v > 0 for v in by_type.values()):
    c1, c2, c3, c4 = st.columns(4)
    type_info = {
        'low_gpa'        : ('📉', 'Low GPA',         c1),
        'high_risk'      : ('🚨', 'High Risk',        c2),
        'low_attendance' : ('📅', 'Low Attendance',   c3),
        'failed_subjects': ('📝', 'Failed Subjects',  c4),
    }
    for key, (icon, label, col) in type_info.items():
        with col:
            st.metric(f"{icon} {label}", by_type.get(key, 0))

st.markdown("---")


# ==============================================================================
# SECTION 2 — SEND NOTIFICATIONS PANEL
# ==============================================================================

st.markdown('<div class="section-header">📤 Send Parent Notifications</div>',
            unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="send-panel">', unsafe_allow_html=True)

    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.markdown("##### 🎯 Select Target Students")

        col_g, col_s = st.columns(2)

        with col_g:
            grade_options = ['All Grades', 'Grade 6', 'Grade 7',
                             'Grade 8', 'Grade 9', 'Grade 10']
            selected_grade = st.selectbox(
                "📚 Grade",
                grade_options,
                key = "notif_grade"
            )

        with col_s:
            section_options = ['All Sections', 'Section A',
                               'Section B', 'Section C']
            selected_section = st.selectbox(
                "🏫 Section",
                section_options,
                key = "notif_section"
            )

        st.markdown("##### ℹ️ What will be checked?")
        st.markdown("""
        - 📉 **Low GPA** → GPA below 50%
        - 🚨 **High Risk** → ML risk level High or Critical
        - 📅 **Low Attendance** → Below 75% in last 30 days
        - 📝 **Failed Subjects** → 2 or more subjects failed
        """)

    with col_right:
        st.markdown("##### 📊 Estimated Reach")

        # Parse selections
        grade   = None
        section = None

        if selected_grade != 'All Grades':
            grade = int(selected_grade.split(' ')[1])
        if selected_section != 'All Sections':
            section = selected_section.split(' ')[1]

        # Get student count estimate
        try:
            count_url = "http://localhost:5000/api/students/count"
            params    = {}
            if grade:
                params['grade'] = grade
            r = requests.get(
                count_url,
                headers = {'Authorization': f'Bearer {token}'},
                params  = params,
                timeout = 5
            )
            if r.status_code == 200:
                total_students = r.json().get('count', 0)
            else:
                total_students = 400
        except Exception:
            total_students = 400

        st.metric("👥 Students to Check", total_students)
        st.info(
            "💡 Only students meeting alert conditions will receive emails. "
            "Cooldown prevents duplicate alerts."
        )

        st.write("")

        # ── SEND BUTTON ────────────────────────────────────────────────────
        send_clicked = st.button(
            "📨 Send Notifications",
            type               = "primary",
            use_container_width = True,
            key                = "send_notif_btn"
        )

    st.markdown('</div>', unsafe_allow_html=True)

# ── Handle Send ────────────────────────────────────────────────────────────────
if send_clicked:
    body = {}
    if grade:
        body['grade']   = grade
    if section:
        body['section'] = section

    label = f"Grade {grade}" if grade else "All Grades"
    if section:
        label += f" - Section {section}"

    with st.spinner(f"⏳ Sending notifications for {label}... (this may take 1-3 minutes)"):
        result = api_post('/api/notifications/bulk-check', body)

    if 'error' in result:
        st.error(f"❌ {result['error']}")
    else:
        st.success("✅ Notification check complete!")

        # ── Results summary ─────────────────────────────────────────────────
        r1, r2, r3, r4 = st.columns(4)
        with r1:
            st.metric("👥 Students Checked",
                      result.get('total_students', 0))
        with r2:
            st.metric("✅ Emails Sent",
                      result.get('sent', 0),
                      delta = f"+{result.get('sent', 0)}")
        with r3:
            st.metric("❌ Failed",
                      result.get('failed', 0))
        with r4:
            st.metric("⏭️ No Trigger",
                      result.get('no_trigger', 0))

        if result.get('sent', 0) > 0:
            st.balloons()
            st.info(
                f"📧 {result.get('sent', 0)} parent(s) have been notified. "
                f"Check notification history below."
            )
        else:
            st.info(
                "ℹ️ No notifications were triggered. "
                "Either all students are performing well or "
                "cooldown is active for recent alerts."
            )

        # Refresh stats
        st.rerun()


st.markdown("---")


# ==============================================================================
# SECTION 3 — MANUAL NOTIFICATION (Per Student)
# ==============================================================================

st.markdown('<div class="section-header">✍️ Send Manual Notification</div>',
            unsafe_allow_html=True)

with st.expander("📮 Send custom message to a specific student's parent",
                 expanded=False):

    col_a, col_b = st.columns(2)

    with col_a:
        student_id_input = st.number_input(
            "🔢 Student ID (Database ID)",
            min_value = 1,
            max_value = 9999,
            value     = 1,
            key       = "manual_student_id"
        )

        notif_type = st.selectbox(
            "📋 Notification Type",
            options = [
                'low_gpa',
                'high_risk',
                'low_attendance',
                'failed_subjects'
            ],
            format_func = lambda x: {
                'low_gpa'        : '📉 Low GPA Alert',
                'high_risk'      : '🚨 High Risk Alert',
                'low_attendance' : '📅 Low Attendance Warning',
                'failed_subjects': '📝 Failed Subjects Alert'
            }.get(x, x),
            key = "manual_notif_type"
        )

    with col_b:
        custom_message = st.text_area(
            "💬 Custom Message",
            placeholder = (
                "e.g. Dear Parent, we would like to inform you that "
                "your child's academic performance needs immediate attention..."
            ),
            height = 120,
            key    = "manual_message"
        )

        send_manual = st.button(
            "📨 Send Manual Notification",
            type               = "primary",
            use_container_width = True,
            key                = "send_manual_btn"
        )

    if send_manual:
        if not custom_message.strip():
            st.error("❌ Please enter a message")
        else:
            with st.spinner("Sending notification..."):
                result = api_post(
                    f'/api/students/{student_id_input}/notify',
                    {
                        'notification_type': notif_type,
                        'message'          : custom_message.strip()
                    }
                )

            if result.get('status') == 'sent':
                st.success(
                    f"✅ Notification sent to "
                    f"{result.get('sent_to', 'parent')} "
                    f"for student {result.get('student', '')}!"
                )
            elif 'error' in result:
                st.error(f"❌ {result['error']}")


st.markdown("---")


# ==============================================================================
# SECTION 4 — NOTIFICATION HISTORY TABLE
# ==============================================================================

st.markdown('<div class="section-header">📋 Notification History</div>',
            unsafe_allow_html=True)

col_filter1, col_filter2, col_refresh = st.columns([2, 2, 1])

with col_filter1:
    history_limit = st.selectbox(
        "Show last",
        [25, 50, 100, 200],
        key = "history_limit"
    )

with col_filter2:
    filter_status = st.selectbox(
        "Filter by Status",
        ['All', 'sent', 'failed', 'pending'],
        key = "filter_status"
    )

with col_refresh:
    st.write("")
    st.write("")
    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()

# ── Fetch notifications ────────────────────────────────────────────────────────
notifications = api_get(f'/api/notifications?limit={history_limit}')

if not notifications:
    st.info("📭 No notifications sent yet. Use the panel above to send notifications.")
else:
    # Filter by status
    if filter_status != 'All':
        notifications = [
            n for n in notifications
            if n.get('status') == filter_status
        ]

    if not notifications:
        st.info(f"No {filter_status} notifications found.")
    else:
        st.markdown(f"**Showing {len(notifications)} notifications**")
        st.write("")

        # ── Type icons & badge HTML ─────────────────────────────────────────
        type_icons = {
            'low_gpa'        : '📉',
            'high_risk'      : '🚨',
            'low_attendance' : '📅',
            'failed_subjects': '📝'
        }

        # ── Build display table ─────────────────────────────────────────────
        for notif in notifications:
            ntype      = notif.get('notification_type', '')
            status     = notif.get('status', '')
            icon       = type_icons.get(ntype, '📧')
            student    = notif.get('student_name', f"Student #{notif.get('student_id')}")
            grade      = notif.get('grade', '')
            section    = notif.get('section', '')
            sent_to    = notif.get('sent_to_email', 'N/A')
            created_at = notif.get('created_at', '')
            reason     = notif.get('trigger_reason', '')

            # Format date
            try:
                dt = datetime.fromisoformat(created_at.replace('Z',''))
                date_str = dt.strftime('%d %b %Y %H:%M')
            except Exception:
                date_str = created_at[:16] if created_at else 'N/A'

            # Status badge color
            badge_color = {
                'sent'   : '#d1fae5',
                'failed' : '#fee2e2',
                'pending': '#fef3c7'
            }.get(status, '#f3f4f6')

            badge_text_color = {
                'sent'   : '#065f46',
                'failed' : '#991b1b',
                'pending': '#92400e'
            }.get(status, '#374151')

            # Type label
            type_labels = {
                'low_gpa'        : 'Low GPA',
                'high_risk'      : 'High Risk',
                'low_attendance' : 'Low Attendance',
                'failed_subjects': 'Failed Subjects'
            }

            with st.container():
                st.markdown(f"""
                <div style="background:white; border-radius:10px; padding:14px 18px;
                            margin-bottom:8px; border-left:4px solid
                            {'#10b981' if status=='sent' else '#ef4444' if status=='failed' else '#f59e0b'};
                            box-shadow:0 1px 4px rgba(0,0,0,0.06);">
                    <div style="display:flex; justify-content:space-between;
                                align-items:center; flex-wrap:wrap; gap:8px;">
                        <div>
                            <span style="font-size:1.1rem;">{icon}</span>
                            <strong style="color:#1a202c; font-size:0.95rem;">
                                {student}
                            </strong>
                            <span style="color:#6b7280; font-size:0.85rem;">
                                &nbsp;|&nbsp; Grade {grade} - {section}
                            </span>
                        </div>
                        <div style="display:flex; gap:8px; align-items:center;">
                            <span style="background:{badge_color}; color:{badge_text_color};
                                         padding:3px 10px; border-radius:20px;
                                         font-size:0.78rem; font-weight:600;">
                                {status.upper()}
                            </span>
                            <span style="color:#9ca3af; font-size:0.82rem;">
                                {date_str}
                            </span>
                        </div>
                    </div>
                    <div style="margin-top:6px;">
                        <span style="color:#6b7280; font-size:0.83rem;">
                            📧 {sent_to} &nbsp;|&nbsp;
                            🏷️ {type_labels.get(ntype, ntype)}
                        </span>
                    </div>
                    <div style="margin-top:4px; color:#374151;
                                font-size:0.85rem; line-height:1.4;">
                        {reason[:120] + '...' if len(reason) > 120 else reason}
                    </div>
                </div>
                """, unsafe_allow_html=True)
