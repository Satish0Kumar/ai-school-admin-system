"""
Attendance Management
ScholarSense - AI-Powered Academic Intelligence System
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import streamlit as st
from frontend.utils.session_manager import SessionManager
from frontend.utils.api_client import APIClient
from datetime import date, timedelta
import pandas as pd

st.set_page_config(
    page_title="Attendance - ScholarSense",
    page_icon="📅",
    layout="wide"
)

from frontend.utils.sidebar import render_sidebar
render_sidebar()
SessionManager.require_auth()
from frontend.utils.ui_helpers import inject_theme_css
inject_theme_css()

st.markdown("""
<style>
    .main { background-color: #f7fafc; padding: 1rem 2rem; }
    .section-header {
        color: #1a202c; font-size: 1.5rem; font-weight: 700;
        margin: 1.5rem 0 1rem 0; padding-bottom: 0.5rem;
        border-bottom: 3px solid #2563eb; display: inline-block;
    }
    .attendance-card {
        background: white; padding: 1rem; border-radius: 10px;
        border: 1px solid #e2e8f0; margin-bottom: 0.75rem;
    }
    .status-present  { background: #c6f6d5; color: #22543d; padding: 0.25rem 0.75rem; border-radius: 12px; font-weight: 600; }
    .status-absent   { background: #fed7d7; color: #742a2a; padding: 0.25rem 0.75rem; border-radius: 12px; font-weight: 600; }
    .status-late     { background: #feebc8; color: #7c2d12; padding: 0.25rem 0.75rem; border-radius: 12px; font-weight: 600; }
    .status-excused  { background: #e2e8f0; color: #2d3748; padding: 0.25rem 0.75rem; border-radius: 12px; font-weight: 600; }
    .edit-row {
        background: white; padding: 0.75rem 1rem; border-radius: 10px;
        border: 1px solid #e2e8f0; margin-bottom: 0.5rem;
    }
    .stButton > button[kind="primary"] { background: #2563eb !important; color: white !important; }
    [data-testid="stSidebar"] { background-color: white; border-right: 1px solid #e2e8f0; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

user = SessionManager.get_user()
st.title("📅 Attendance Management")
st.markdown("Track and manage student attendance")

# 4 tabs now
tab1, tab2, tab3, tab4 = st.tabs([
    "📝 Mark Attendance",
    "📊 Attendance Reports",
    "⚠️ Low Attendance",
    "✏️ Edit Attendance"
])

# ============================================
# TAB 1: MARK ATTENDANCE
# ============================================
with tab1:
    st.markdown('<p class="section-header">📝 Mark Daily Attendance</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        selected_date = st.date_input("Select Date", value=date.today(), max_value=date.today())
    with col2:
        grade_filter = st.selectbox("Grade", ["All"] + list(range(6, 11)), key="mark_grade")
    with col3:
        section_filter = st.selectbox("Section", ["All", "A", "B", "C"], key="mark_section")
    
    with st.spinner("Loading students..."):
        grade   = None if grade_filter   == "All" else int(grade_filter)
        section = None if section_filter == "All" else section_filter
        daily_attendance = APIClient.get_daily_attendance(
            date=str(selected_date), grade=grade, section=section
        )
        if not daily_attendance:
            st.warning(f"🔍 Debug: API returned {len(daily_attendance) if daily_attendance else 0} students for Grade={grade}, Section={section}")

    if daily_attendance:
        st.markdown(f"**Students to mark:** {len(daily_attendance)}")
        attendance_data = []
        
        for idx, student_data in enumerate(daily_attendance):
            student    = student_data
            attendance = student_data.get('attendance', {})
            current_status = attendance.get('status', 'not_marked')
            
            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
            with col1:
                st.markdown(f"**{student['first_name']} {student['last_name']}**")
                st.markdown(f"<small>ID: {student['student_id']} | Grade: {student['grade']}-{student['section']}</small>", unsafe_allow_html=True)
            with col2:
                status_options = ['present', 'absent', 'late', 'excused']
                default_idx = status_options.index(current_status) if current_status in status_options else 0
                status = st.selectbox(
                    "Status", options=status_options, index=default_idx,
                    key=f"status_{student['id']}", label_visibility="collapsed"
                )
            with col3:
                remarks = st.text_input(
                    "Remarks", value=attendance.get('remarks', ''),
                    key=f"remarks_{student['id']}", placeholder="Optional notes",
                    label_visibility="collapsed"
                )
            with col4:
                if current_status != 'not_marked':
                    st.markdown(f'<span class="status-{current_status}">Marked</span>', unsafe_allow_html=True)
            
            attendance_data.append({
                'student_id': student['id'],
                'date':       str(selected_date),
                'status':     status,
                'remarks':    remarks if remarks else None
            })
            st.markdown("<hr style='margin: 0.5rem 0; border-color: #e2e8f0;'>", unsafe_allow_html=True)
        
        if st.button("💾 Save Attendance", type="primary", use_container_width=True):
            with st.spinner("Saving attendance..."):
                result = APIClient.mark_bulk_attendance(attendance_data)
            if 'error' not in result:
                st.success(f"✅ {result['message']}")
                st.balloons()
                st.rerun()
            else:
                st.error(f"❌ {result['error']}")
    else:
        st.info("📭 No students found for the selected filters")

# ============================================
# TAB 2: ATTENDANCE REPORTS
# ============================================
with tab2:
    st.markdown('<p class="section-header">📊 Attendance Reports</p>', unsafe_allow_html=True)
    
    students = APIClient.get_students()
    if students:
        col1, col2 = st.columns([3, 1])
        with col1:
            student_options = {f"{s['first_name']} {s['last_name']} ({s['student_id']})": s['id'] for s in students}
            selected_student = st.selectbox("Select Student", list(student_options.keys()))
            student_id = student_options[selected_student]
        with col2:
            days_filter = st.selectbox("Period", [7, 14, 30, 60, 90], index=2, format_func=lambda x: f"Last {x} days")
        
        with st.spinner("Loading attendance data..."):
            stats = APIClient.get_attendance_stats(student_id, days=days_filter)
        
        if stats and 'error' not in stats:
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1: st.metric("Total Days", stats['total_days'])
            with col2: st.metric("Present", stats['present'])
            with col3: st.metric("Absent",  stats['absent'],  delta=f"-{stats['absent']}"  if stats['absent']  > 0 else "0")
            with col4: st.metric("Late",    stats['late'])
            with col5:
                att_color = "normal" if stats['attendance_rate'] >= 75 else "inverse"
                st.metric("Attendance Rate", f"{stats['attendance_rate']}%", delta_color=att_color)
            
            st.markdown("### 📋 Detailed Records")
            start_date = str(date.today() - timedelta(days=days_filter))
            end_date   = str(date.today())
            records = APIClient.get_student_attendance(student_id, start_date, end_date)
            
            if records:
                df = pd.DataFrame(records)
                df = df[['attendance_date', 'status', 'remarks']].sort_values('attendance_date', ascending=False)
                df.columns = ['Date', 'Status', 'Remarks']
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("No attendance records found for this period")
        else:
            st.warning("Unable to load attendance statistics")

# ============================================
# TAB 3: LOW ATTENDANCE ALERT
# ============================================
with tab3:
    st.markdown('<p class="section-header">⚠️ Low Attendance Alert</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 3])
    with col1:
        threshold = st.slider("Attendance Threshold (%)", min_value=50, max_value=90, value=75, step=5)
    with col2:
        alert_days = st.selectbox("Check Period", [30, 60, 90], format_func=lambda x: f"Last {x} days")
    
    with st.spinner("Finding students with low attendance..."):
        low_attendance = APIClient.get_low_attendance_students(threshold=threshold, days=alert_days)
    
    if low_attendance:
        st.warning(f"⚠️ Found {len(low_attendance)} students below {threshold}% attendance")
        for item in low_attendance:
            student = item['student']
            stats   = item['attendance_stats']
            with st.container():
                col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 1])
                with col1:
                    st.markdown(f"**{student['first_name']} {student['last_name']}**")
                    st.markdown(f"<small>ID: {student['student_id']} | Grade: {student['grade']}-{student['section']}</small>", unsafe_allow_html=True)
                with col2: st.markdown(f"**Attendance:** {stats['attendance_rate']}%")
                with col3: st.markdown(f"Present: {stats['present']}/{stats['total_days']}")
                with col4: st.markdown(f"Absent: {stats['absent']}")
                with col5:
                    if st.button("View", key=f"view_low_{student['id']}", use_container_width=True):
                        st.session_state['selected_student_id'] = student['id']
                        st.switch_page("pages/3_👤_Student_Profile.py")
                st.markdown("<hr style='margin: 0.5rem 0; border-color: #e2e8f0;'>", unsafe_allow_html=True)
    else:
        st.success(f"✅ All students have attendance above {threshold}%! Excellent! 🎉")

# ============================================
# TAB 4: EDIT ATTENDANCE
# ============================================
with tab4:
    st.markdown('<p class="section-header">✏️ Edit Attendance</p>', unsafe_allow_html=True)
    st.markdown("Select a student and date range to view, edit or delete existing attendance records.")

    # ── Filters ─────────────────────────────────────────────────────────────
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        edit_students = APIClient.get_students()
        if not edit_students:
            st.warning("⚠️ No students found.")
            st.stop()
        edit_student_options = {
            f"{s['first_name']} {s['last_name']} ({s['student_id']})": s['id']
            for s in edit_students
        }
        edit_selected = st.selectbox("Select Student", list(edit_student_options.keys()), key="edit_student_select")
        edit_student_id = edit_student_options[edit_selected]

    with col2:
        edit_start = st.date_input(
            "From", value=date.today() - timedelta(days=30),
            max_value=date.today(), key="edit_start_date"
        )
    with col3:
        edit_end = st.date_input(
            "To", value=date.today(),
            max_value=date.today(), key="edit_end_date"
        )

    if edit_start > edit_end:
        st.error("❌ 'From' date cannot be after 'To' date.")
        st.stop()

    # ── Load records ─────────────────────────────────────────────────────────
    with st.spinner("Loading attendance records..."):
        records = APIClient.get_student_attendance(
            edit_student_id,
            start_date=str(edit_start),
            end_date=str(edit_end)
        )

    if not records:
        st.info("📭 No attendance records found for this student in the selected date range.")
    else:
        # Sort newest first
        records_sorted = sorted(records, key=lambda r: r.get('attendance_date', ''), reverse=True)

        STATUS_OPTIONS   = ['present', 'absent', 'late', 'excused']
        STATUS_EMOJI     = {'present': '🟢', 'absent': '🔴', 'late': '🟠', 'excused': '⚪'}
        STATUS_COLOR_CSS = {
            'present': 'status-present',
            'absent' : 'status-absent',
            'late'   : 'status-late',
            'excused': 'status-excused'
        }

        st.markdown(f"ℹ️ **{len(records_sorted)} record(s) found** for "
                    f"**{edit_selected.split('(')[0].strip()}** "
                    f"({str(edit_start)} → {str(edit_end)})")
        st.markdown("---")

        # Column headers
        hc1, hc2, hc3, hc4, hc5 = st.columns([2, 2, 3, 1, 1])
        hc1.markdown("**📅 Date**")
        hc2.markdown("**📊 Status**")
        hc3.markdown("**💬 Remarks**")
        hc4.markdown("**✅ Save**")
        hc5.markdown("**🗑️ Delete**")
        st.markdown("<hr style='margin:0.3rem 0; border-color:#cbd5e0;'>", unsafe_allow_html=True)

        for rec in records_sorted:
            rec_id     = rec.get('id') or rec.get('attendance_id')
            rec_date   = rec.get('attendance_date', 'N/A')
            rec_status = rec.get('status', 'present')
            rec_remark = rec.get('remarks', '') or ''

            c1, c2, c3, c4, c5 = st.columns([2, 2, 3, 1, 1])

            with c1:
                st.markdown(f"📅 **{rec_date}**")

            with c2:
                cur_idx = STATUS_OPTIONS.index(rec_status) if rec_status in STATUS_OPTIONS else 0
                new_status = st.selectbox(
                    "Status",
                    options=STATUS_OPTIONS,
                    index=cur_idx,
                    key=f"edit_status_{rec_id}",
                    label_visibility="collapsed",
                    format_func=lambda s: f"{STATUS_EMOJI.get(s, '')} {s.capitalize()}"
                )

            with c3:
                new_remark = st.text_input(
                    "Remarks",
                    value=rec_remark,
                    key=f"edit_remark_{rec_id}",
                    placeholder="Optional note...",
                    label_visibility="collapsed"
                )

            with c4:
                if st.button("✅", key=f"save_{rec_id}", help="Save changes", use_container_width=True):
                    with st.spinner("Saving..."):
                        result = APIClient.update_attendance(
                            rec_id,
                            status=new_status,
                            remarks=new_remark if new_remark else None
                        )
                    if 'error' not in result:
                        st.success(f"✅ Updated {rec_date} → **{new_status}**")
                        st.rerun()
                    else:
                        st.error(f"❌ {result['error']}")

            with c5:
                if st.button("🗑️", key=f"del_{rec_id}", help="Delete record", use_container_width=True):
                    with st.spinner("Deleting..."):
                        result = APIClient.delete_attendance(rec_id)
                    if 'error' not in result:
                        st.success(f"✅ Deleted record for {rec_date}")
                        st.rerun()
                    else:
                        st.error(f"❌ {result['error']}")

            st.markdown("<hr style='margin:0.3rem 0; border-color:#e2e8f0;'>", unsafe_allow_html=True)
