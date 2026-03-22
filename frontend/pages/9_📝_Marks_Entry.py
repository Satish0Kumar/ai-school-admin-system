"""
Marks Entry Module
ScholarSense - AI-Powered Academic Intelligence System
Enhancement 6: Marks Entry - Enter Marks, Analytics, Failed Students
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, date
from frontend.utils.session_manager import SessionManager

# ============================================
# PAGE CONFIG
# ============================================
st.set_page_config(
    page_title="Marks Entry - ScholarSense",
    page_icon="📝",
    layout="wide"
)

from frontend.utils.sidebar import render_sidebar
render_sidebar()

from frontend.utils.ui_helpers import inject_theme_css
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
    .score-card {
        background: white; padding: 1.2rem; border-radius: 12px;
        border: 1px solid #e2e8f0; text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    .score-label {
        font-size: 0.8rem; color: #4a5568;
        font-weight: 600; text-transform: uppercase;
    }
    .score-value {
        font-size: 1.8rem; font-weight: 800; margin: 0.25rem 0;
    }
    .pass  { color: #00CC44; }
    .fail  { color: #FF4B4B; }
    .kpi-card {
        background: white; padding: 1.2rem 1.5rem;
        border-radius: 12px; border: 1px solid #e2e8f0;
        text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    .kpi-value { font-size: 2rem; font-weight: 800; margin: 0.2rem 0; }
    .kpi-label { font-size: 0.8rem; color: #4a5568;
                 font-weight: 600; text-transform: uppercase; }
    [data-testid="stSidebar"] {
        background-color: white; border-right: 1px solid #e2e8f0;
    }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ============================================
# CONSTANTS
# ============================================
API_BASE   = "http://localhost:5000/api"
PASS_MARK  = 35.0

EXAM_TYPES = [
    'Unit Test 1', 'Unit Test 2',
    'Mid Term', 'Final Exam',
    'Assignment', 'Other'
]

SEMESTERS = [
    '2025-2026 Sem 1', '2025-2026 Sem 2',
    '2024-2025 Sem 1', '2024-2025 Sem 2'
]

SUBJECTS = {
    'math_score':     '🔢 Mathematics',
    'science_score':  '🔬 Science',
    'english_score':  '📖 English',
    'social_score':   '🌍 Social Studies',
    'language_score': '🗣️ Language'
}

GRADES   = [6, 7, 8, 9, 10]
SECTIONS = ['A', 'B', 'C', 'D', 'All']

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
            timeout=10
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
            timeout=10
        )
        return r.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}

def api_put(endpoint, payload):
    try:
        r = requests.put(
            f"{API_BASE}{endpoint}",
            headers=get_headers(),
            json=payload,
            timeout=10
        )
        return r.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_students_by_grade(grade, section=None):
    """Fetch students filtered by grade/section"""
    params = {"grade": grade}
    if section and section != 'All':
        params['section'] = section
    res = api_get("/students", params=params)
    if isinstance(res, list):
        return res
    return []

def score_color(score):
    """Return pass/fail CSS class"""
    if score is None:
        return ''
    return 'pass' if float(score) >= PASS_MARK else 'fail'

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
        <p style="margin:0; font-weight:700; color:#1a202c;">{user['full_name']}</p>
        <p style="margin:0.25rem 0 0 0; color:#4a5568;
                  font-size:0.9rem;">{user['role'].title()}</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### 📚 Navigation")
    if st.button("📊 Dashboard",          use_container_width=True):
        st.switch_page("pages/1_📊_Dashboard.py")
    if st.button("👥 Students",           use_container_width=True):
        st.switch_page("pages/2_👥_Students.py")
    if st.button("🎯 Predictions",        use_container_width=True):
        st.switch_page("pages/4_🎯_Predictions.py")
    if st.button("📝 Incident Logging",   use_container_width=True):
        st.switch_page("pages/6_📝_Incident_Logging.py")
    if st.button("🧠 Behavioral Dashboard", use_container_width=True):
        st.switch_page("pages/8_🧠_Behavioral_Dashboard.py")
    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True, type="primary"):
        SessionManager.logout()
        st.switch_page("app.py")

# ============================================
# PAGE HEADER
# ============================================
st.markdown("""
    <h1 style='color:#1a202c; margin-bottom:0;'>📝 Marks Entry Module</h1>
    <p style='color:#4a5568; margin-top:0.25rem;'>
        Enter student marks → Auto-calculates GPA → Feeds ML prediction model
    </p>
    <hr style='border:none; border-top:1px solid #e2e8f0; margin:1rem 0;'/>
""", unsafe_allow_html=True)

# ============================================
# TABS
# ============================================
tab1, tab2, tab3 = st.tabs([
    "✏️ Enter Marks",
    "📊 Analytics",
    "⚠️ Failed Students"
])


# ============================================================
# TAB 1 — ENTER MARKS
# ============================================================
with tab1:
    st.markdown("### ✏️ Enter Student Marks")
    st.markdown("Select a student, choose exam details, enter scores and submit.")
    st.markdown("---")

    # ── Step 1: Select Class ───────────────────────────────
    st.markdown("#### 📌 Step 1 — Select Class")
    s1c1, s1c2, s1c3 = st.columns(3)

    with s1c1:
        sel_grade = st.selectbox(
            "🎓 Grade *",
            options=GRADES,
            index=2   # default Grade 8
        )
    with s1c2:
        sel_section = st.selectbox(
            "🏫 Section",
            options=SECTIONS,
            index=0
        )
    with s1c3:
        sel_semester = st.selectbox(
            "📅 Semester *",
            options=SEMESTERS,
            index=0
        )

    # ── Step 2: Select Student ─────────────────────────────
    st.markdown("#### 👤 Step 2 — Select Student")

    with st.spinner("Loading students..."):
        students = get_students_by_grade(
            sel_grade,
            sel_section if sel_section != 'All' else None
        )

    if not students:
        st.warning("⚠️ No students found for the selected grade/section.")
        st.stop()

    student_options = {
        f"{s['student_id']} — {s['first_name']} {s['last_name']} "
        f"(Grade {s['grade']}{s.get('section', '')})": s['id']
        for s in students
    }

    s2c1, s2c2 = st.columns([3, 1])
    with s2c1:
        sel_student_label = st.selectbox(
            "👤 Student *",
            options=list(student_options.keys())
        )
    with s2c2:
        sel_exam_type = st.selectbox(
            "📋 Exam Type *",
            options=EXAM_TYPES,
            index=2   # default Mid Term
        )

    sel_student_id = student_options[sel_student_label]

    st.markdown("---")

    # ── Step 3: Enter Scores ───────────────────────────────
    st.markdown("#### 🔢 Step 3 — Enter Subject Scores (out of 100)")
    st.caption(f"⚡ Pass mark: **{int(PASS_MARK)}** | GPA auto-calculated as average of all 5 subjects")

    with st.form("marks_entry_form", clear_on_submit=False):
        sc1, sc2, sc3, sc4, sc5 = st.columns(5)

        with sc1:
            math_score = st.number_input(
                "🔢 Mathematics",
                min_value=0.0, max_value=100.0,
                value=0.0, step=0.5,
                format="%.1f"
            )
        with sc2:
            science_score = st.number_input(
                "🔬 Science",
                min_value=0.0, max_value=100.0,
                value=0.0, step=0.5,
                format="%.1f"
            )
        with sc3:
            english_score = st.number_input(
                "📖 English",
                min_value=0.0, max_value=100.0,
                value=0.0, step=0.5,
                format="%.1f"
            )
        with sc4:
            social_score = st.number_input(
                "🌍 Social Studies",
                min_value=0.0, max_value=100.0,
                value=0.0, step=0.5,
                format="%.1f"
            )
        with sc5:
            language_score = st.number_input(
                "🗣️ Language",
                min_value=0.0, max_value=100.0,
                value=0.0, step=0.5,
                format="%.1f"
            )

        # ── Assignment rate + Remarks ──────────────────────
        r1c1, r1c2 = st.columns([1, 2])
        with r1c1:
            assignment_rate = st.slider(
                "📚 Assignment Submission Rate (%)",
                min_value=0, max_value=100,
                value=100, step=5
            )
        with r1c2:
            remarks = st.text_input(
                "🗒️ Remarks (optional)",
                placeholder="e.g., Absent for Science paper, re-test scheduled..."
            )

        st.markdown("---")

        # ── Live Preview ───────────────────────────────────
        all_scores   = [math_score, science_score, english_score,
                        social_score, language_score]
        live_gpa     = round(sum(all_scores) / 5, 2)
        live_total   = round(sum(all_scores), 2)
        live_failed  = sum(1 for s in all_scores if s < PASS_MARK)
        live_result  = "✅ PASS" if live_failed == 0 else f"❌ FAIL ({live_failed} subject{'s' if live_failed > 1 else ''})"

        st.markdown("##### 👁️ Live Preview")
        pv1, pv2, pv3, pv4 = st.columns(4)
        pv1.metric("📊 GPA",           f"{live_gpa}%")
        pv2.metric("🔢 Total Marks",   f"{live_total}/500")
        pv3.metric("❌ Failed Subjects", live_failed)
        pv4.metric("🏆 Result",         live_result)

        # Subject pass/fail indicators
        subj_names  = ["Math", "Science", "English", "Social", "Language"]
        ind_cols    = st.columns(5)
        for idx, (col, score, name) in enumerate(
            zip(ind_cols, all_scores, subj_names)
        ):
            status = "🟢" if score >= PASS_MARK else "🔴"
            col.markdown(
                f"<div style='text-align:center; font-size:0.85rem;'>"
                f"{status} <b>{name}</b><br/>{score:.1f}%</div>",
                unsafe_allow_html=True
            )

        st.markdown("---")
        submit_btn = st.form_submit_button(
            "💾 Save Marks",
            use_container_width=True,
            type="primary"
        )

    # ── Handle Submission ──────────────────────────────────
    if submit_btn:
        payload = {
            "student_id":                sel_student_id,
            "semester":                  sel_semester,
            "exam_type":                 sel_exam_type,
            "math_score":                math_score,
            "science_score":             science_score,
            "english_score":             english_score,
            "social_score":              social_score,
            "language_score":            language_score,
            "assignment_submission_rate": float(assignment_rate),
            "remarks":                   remarks.strip() or None
        }

        with st.spinner("💾 Saving marks..."):
            result = api_post("/marks/entry", payload)

        if result.get('status') == 'success':
            action = result.get('action', 'saved')
            st.success(f"✅ Marks {action} successfully!")
            st.balloons()

            # Show result summary
            rec = result['data']
            st.markdown(f"""
            <div style='background:#f0fff4; padding:1rem 1.5rem;
                        border-radius:10px; border-left:5px solid #00CC44;
                        margin-top:1rem;'>
                <b>📋 Marks Summary</b><br/>
                👤 Student: <b>{sel_student_label.split(' — ')[0]}</b> &nbsp;|&nbsp;
                📋 Exam: <b>{sel_exam_type}</b> &nbsp;|&nbsp;
                📅 Semester: <b>{sel_semester}</b><br/>
                📊 GPA: <b>{rec.get('gpa')}%</b> &nbsp;|&nbsp;
                🔢 Total: <b>{rec.get('total_marks')}/500</b> &nbsp;|&nbsp;
                ❌ Failed: <b>{rec.get('failed_subjects')} subject(s)</b><br/>
                🤖 <i>Academic records updated → ML model will use latest scores</i>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.error(f"❌ Failed: {result.get('message', 'Unknown error')}")


# ============================================================
# TAB 2 — ANALYTICS
# ============================================================
with tab2:
    st.markdown("### 📊 Class Performance Analytics")
    st.markdown("---")

    # ── Filters ───────────────────────────────────────────
    st.markdown("#### 🔍 Select Class to Analyse")
    a1, a2, a3 = st.columns(3)

    with a1:
        an_grade = st.selectbox(
            "🎓 Grade",
            options=GRADES,
            index=2,
            key="an_grade"
        )
    with a2:
        an_section = st.selectbox(
            "🏫 Section",
            options=SECTIONS,
            index=0,
            key="an_section"
        )
    with a3:
        st.markdown("<br/>", unsafe_allow_html=True)
        an_refresh = st.button(
            "🔄 Load Analytics",
            use_container_width=True,
            type="primary",
            key="an_refresh"
        )

    st.markdown("---")

    # ── Fetch stats ────────────────────────────────────────
    section_param = None if an_section == 'All' else an_section

    with st.spinner("📊 Loading analytics..."):
        stats_result = api_get(
            f"/marks/stats/{an_grade}",
            params={"section": section_param}
        )

    if stats_result.get('status') != 'success':
        st.error(f"❌ {stats_result.get('message', 'Could not load analytics')}")
    else:
        stats = stats_result.get('data', {})

        if stats.get('total_students', 0) == 0:
            st.info(f"ℹ️ No marks data found for Grade {an_grade}"
                    f"{f' Section {an_section}' if an_section != 'All' else ''}. "
                    f"Enter marks in Tab 1 first.")
        else:
            # ── KPI Row ────────────────────────────────────
            st.markdown('<p class="section-header">📈 Class Overview</p>',
                        unsafe_allow_html=True)

            k1, k2, k3, k4, k5 = st.columns(5)

            with k1:
                st.markdown(f"""
                <div class="kpi-card" style="border-top:4px solid #1f77b4;">
                    <p class="kpi-label">👥 Total Students</p>
                    <p class="kpi-value" style="color:#1f77b4;">
                        {stats['total_students']}
                    </p>
                </div>
                """, unsafe_allow_html=True)

            with k2:
                st.markdown(f"""
                <div class="kpi-card" style="border-top:4px solid #00CC44;">
                    <p class="kpi-label">📊 Class Average GPA</p>
                    <p class="kpi-value" style="color:#00CC44;">
                        {stats['avg_gpa']}%
                    </p>
                </div>
                """, unsafe_allow_html=True)

            with k3:
                st.markdown(f"""
                <div class="kpi-card" style="border-top:4px solid #2563eb;">
                    <p class="kpi-label">🏆 Highest GPA</p>
                    <p class="kpi-value" style="color:#2563eb;">
                        {stats['highest_gpa']}%
                    </p>
                </div>
                """, unsafe_allow_html=True)

            with k4:
                st.markdown(f"""
                <div class="kpi-card" style="border-top:4px solid #FFA500;">
                    <p class="kpi-label">📉 Lowest GPA</p>
                    <p class="kpi-value" style="color:#FFA500;">
                        {stats['lowest_gpa']}%
                    </p>
                </div>
                """, unsafe_allow_html=True)

            with k5:
                st.markdown(f"""
                <div class="kpi-card" style="border-top:4px solid #FF4B4B;">
                    <p class="kpi-label">❌ Students Failed</p>
                    <p class="kpi-value" style="color:#FF4B4B;">
                        {stats['total_failed']}
                    </p>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("---")

            # ── Row 2: Subject Averages + GPA Distribution ──
            st.markdown('<p class="section-header">📚 Subject & GPA Analysis</p>',
                        unsafe_allow_html=True)

            ch1, ch2 = st.columns(2)

            # Subject averages bar chart
            with ch1:
                subj_avgs = stats.get('subject_averages', {})

                if subj_avgs:
                    subj_names  = list(subj_avgs.keys())
                    subj_values = list(subj_avgs.values())
                    bar_colors  = [
                        '#00CC44' if v >= PASS_MARK else '#FF4B4B'
                        for v in subj_values
                    ]

                    fig_subj = go.Figure(data=[go.Bar(
                        x=subj_names,
                        y=subj_values,
                        marker_color=bar_colors,
                        text=[f"{v}%" for v in subj_values],
                        textposition='outside',
                        width=0.5,
                        hovertemplate='<b>%{x}</b><br>Avg: %{y}%<extra></extra>'
                    )])

                    # Pass mark reference line
                    fig_subj.add_hline(
                        y=PASS_MARK,
                        line_dash="dash",
                        line_color="#FF4B4B",
                        annotation_text=f"Pass Mark ({int(PASS_MARK)}%)",
                        annotation_position="top right"
                    )

                    fig_subj.update_layout(
                        title=dict(
                            text="📚 Subject-wise Average Scores",
                            font=dict(size=14, color='#1a202c')
                        ),
                        height=340,
                        xaxis=dict(title='Subject', showgrid=False),
                        yaxis=dict(
                            title='Average Score (%)',
                            range=[0, 110],
                            showgrid=True,
                            gridcolor='#f0f0f0'
                        ),
                        plot_bgcolor='white',
                        paper_bgcolor='white',
                        font=dict(color='#1a202c'),
                        margin=dict(t=50, b=40, l=50, r=20)
                    )
                    st.plotly_chart(fig_subj, use_container_width=True)

            # GPA distribution donut chart
            with ch2:
                gpa_dist = stats.get('gpa_distribution', {})

                if gpa_dist:
                    dist_labels = list(gpa_dist.keys())
                    dist_values = list(gpa_dist.values())
                    dist_colors = [
                        '#2563eb', '#00CC44',
                        '#FFA500', '#f59e0b', '#FF4B4B'
                    ]

                    fig_dist = go.Figure(data=[go.Pie(
                        labels=dist_labels,
                        values=dist_values,
                        marker=dict(colors=dist_colors),
                        hole=0.45,
                        textinfo='label+value',
                        textfont=dict(size=11),
                        hovertemplate=(
                            '<b>%{label}</b><br>'
                            'Students: %{value}<br>'
                            '%{percent}<extra></extra>'
                        )
                    )])

                    fig_dist.update_layout(
                        title=dict(
                            text="🎓 GPA Distribution",
                            font=dict(size=14, color='#1a202c')
                        ),
                        height=340,
                        plot_bgcolor='white',
                        paper_bgcolor='white',
                        font=dict(color='#1a202c'),
                        legend=dict(
                            orientation='v',
                            x=1.02, y=0.5,
                            font=dict(size=10)
                        ),
                        margin=dict(t=50, b=20, l=10, r=10)
                    )
                    st.plotly_chart(fig_dist, use_container_width=True)

            st.markdown("---")

            # ── Top 5 Performers Table ─────────────────────
            st.markdown('<p class="section-header">🏆 Top 5 Performers</p>',
                        unsafe_allow_html=True)

            top5 = stats.get('top_performers', [])
            if top5:
                top5_rows = []
                for rank, s in enumerate(top5, 1):
                    medal = {1: '🥇', 2: '🥈', 3: '🥉'}.get(rank, f'#{rank}')
                    top5_rows.append({
                        'Rank':         medal,
                        'Student Name': s.get('student_name'),
                        'Student ID':   s.get('student_code'),
                        'GPA':          f"{s.get('gpa', 0):.2f}%",
                        'Total Marks':  f"{s.get('total_marks', 0):.1f}/500"
                    })

                top5_df = pd.DataFrame(top5_rows)
                st.dataframe(
                    top5_df,
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("ℹ️ No top performer data available.")

            st.markdown("---")

            # ── Full Class Marks Table ─────────────────────
            st.markdown('<p class="section-header">📋 Full Class Marks</p>',
                        unsafe_allow_html=True)

            with st.spinner("Loading class marks..."):
                class_result = api_get(
                    f"/marks/{an_grade}/{an_section}"
                )

            if class_result.get('status') == 'success':
                class_marks = class_result['data'].get('marks', [])

                if class_marks:
                    class_rows = []
                    for m in class_marks:
                        class_rows.append({
                            'Rank':       m.get('rank'),
                            'Student':    m.get('student_name'),
                            'ID':         m.get('student_code'),
                            'Math':       m.get('math_score'),
                            'Science':    m.get('science_score'),
                            'English':    m.get('english_score'),
                            'Social':     m.get('social_score'),
                            'Language':   m.get('language_score'),
                            'GPA':        m.get('gpa'),
                            'Total':      m.get('total_marks'),
                            'Failed Subs':m.get('failed_subjects'),
                            'Exam':       m.get('exam_type'),
                            'Semester':   m.get('semester')
                        })

                    class_df = pd.DataFrame(class_rows)

                    # Highlight failed GPA rows
                    def highlight_failed(row):
                        if row.get('Failed Subs', 0) and int(row['Failed Subs']) > 0:
                            return ['background-color: #fff5f5'] * len(row)
                        return [''] * len(row)

                    styled_class = class_df.style.apply(
                        highlight_failed, axis=1
                    )
                    st.dataframe(
                        styled_class,
                        use_container_width=True,
                        hide_index=True
                    )

                    # CSV export
                    csv = class_df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Export Class Marks as CSV",
                        data=csv,
                        file_name=(
                            f"grade{an_grade}_"
                            f"{an_section}_marks_"
                            f"{date.today().isoformat()}.csv"
                        ),
                        mime="text/csv",
                        use_container_width=True
                    )
                else:
                    st.info("ℹ️ No marks records found.")
            else:
                st.error("❌ Could not load class marks.")


# ============================================================
# TAB 3 — FAILED STUDENTS
# ============================================================
with tab3:
    st.markdown("### ⚠️ Failed Students Report")
    st.markdown("Students who scored below the pass mark in one or more subjects.")
    st.markdown("---")

    # ── Filters ───────────────────────────────────────────
    f1, f2, f3 = st.columns(3)

    with f1:
        fail_grade = st.selectbox(
            "🎓 Grade",
            options=['All Grades'] + GRADES,
            key="fail_grade"
        )
    with f2:
        fail_semester = st.selectbox(
            "📅 Semester",
            options=['All Semesters'] + SEMESTERS,
            key="fail_semester"
        )
    with f3:
        st.markdown("<br/>", unsafe_allow_html=True)
        fail_refresh = st.button(
            "🔄 Load Failed Students",
            use_container_width=True,
            type="primary",
            key="fail_refresh"
        )

    st.markdown("---")

    # ── Fetch failed students ──────────────────────────────
    fail_params = {}
    if fail_grade != 'All Grades':
        fail_params['grade'] = fail_grade
    if fail_semester != 'All Semesters':
        fail_params['semester'] = fail_semester

    with st.spinner("Loading failed students..."):
        fail_result = api_get("/marks/failed", params=fail_params)

    if fail_result.get('status') != 'success':
        st.error(f"❌ {fail_result.get('message', 'Could not load data')}")
    else:
        fail_data     = fail_result.get('data', {})
        failed_list   = fail_data.get('failed_students', [])
        total_failed  = fail_data.get('total', 0)

        # ── Summary metrics ────────────────────────────────
        fm1, fm2, fm3, fm4 = st.columns(4)

        fm1.metric("⚠️ Total Failed Students", total_failed)
        fm2.metric(
            "🔴 Failed 3+ Subjects",
            sum(1 for s in failed_list if s.get('failed_subjects', 0) >= 3)
        )
        fm3.metric(
            "🟠 Failed 2 Subjects",
            sum(1 for s in failed_list if s.get('failed_subjects', 0) == 2)
        )
        fm4.metric(
            "🟡 Failed 1 Subject",
            sum(1 for s in failed_list if s.get('failed_subjects', 0) == 1)
        )

        st.markdown("---")

        if not failed_list:
            st.success("🎉 No failed students found for the selected filters!")
        else:
            # ── Failed students expandable cards ───────────
            st.markdown(
                f'<p class="section-header">'
                f'⚠️ {total_failed} Student(s) Need Attention'
                f'</p>',
                unsafe_allow_html=True
            )

            for student in failed_list:
                failed_count  = student.get('failed_subjects', 0)
                failed_details= student.get('failed_details', [])

                # Severity badge
                if failed_count >= 3:
                    badge = "🔴 Critical"
                    color = "#FF4B4B"
                elif failed_count == 2:
                    badge = "🟠 Moderate"
                    color = "#FFA500"
                else:
                    badge = "🟡 Minor"
                    color = "#f59e0b"

                with st.expander(
                    f"{badge}  |  {student.get('student_name')}  "
                    f"({student.get('student_code')})  |  "
                    f"Grade {student.get('grade')}"
                    f"{student.get('section', '')}  |  "
                    f"GPA: {student.get('gpa')}%  |  "
                    f"Failed: {failed_count} subject(s)",
                    expanded=failed_count >= 3
                ):
                    fc1, fc2 = st.columns(2)

                    with fc1:
                        st.markdown(f"**👤 Student:** {student.get('student_name')}")
                        st.markdown(f"**🆔 ID:** {student.get('student_code')}")
                        st.markdown(f"**🎓 Grade:** {student.get('grade')}"
                                    f"{student.get('section', '')}")
                        st.markdown(f"**📊 GPA:** {student.get('gpa')}%")
                        st.markdown(f"**📋 Exam:** {student.get('exam_type')}")
                        st.markdown(f"**📅 Semester:** {student.get('semester')}")

                    with fc2:
                        st.markdown("**❌ Failed Subjects:**")
                        for fd in failed_details:
                            st.markdown(
                                f"- **{fd['subject']}**: "
                                f"{fd['score']}% "
                                f"_(need {fd['deficit']:.1f} more marks to pass)_"
                            )

                        if student.get('parent_email'):
                            st.markdown(
                                f"**📧 Parent Email:** "
                                f"`{student.get('parent_email')}`"
                            )

                    # Subject-wise mini bar chart
                    subj_scores = {
                        'Math':     student.get('math_score'),
                        'Science':  student.get('science_score'),
                        'English':  student.get('english_score'),
                        'Social':   student.get('social_score'),
                        'Language': student.get('language_score')
                    }
                    valid_scores = {
                        k: float(v) for k, v in subj_scores.items()
                        if v is not None
                    }

                    if valid_scores:
                        bar_cols = [
                            '#00CC44' if v >= PASS_MARK else '#FF4B4B'
                            for v in valid_scores.values()
                        ]
                        fig_mini = go.Figure(data=[go.Bar(
                            x=list(valid_scores.keys()),
                            y=list(valid_scores.values()),
                            marker_color=bar_cols,
                            text=[f"{v:.1f}%" for v in valid_scores.values()],
                            textposition='outside'
                        )])
                        fig_mini.add_hline(
                            y=PASS_MARK,
                            line_dash="dash",
                            line_color="#FF4B4B",
                            annotation_text="Pass Mark"
                        )
                        fig_mini.update_layout(
                            height=220,
                            margin=dict(t=20, b=20, l=30, r=20),
                            yaxis=dict(range=[0, 110]),
                            plot_bgcolor='white',
                            paper_bgcolor='white',
                            font=dict(size=11, color='#1a202c'),
                            showlegend=False
                        )
                        st.plotly_chart(fig_mini, use_container_width=True)

            st.markdown("---")

            # ── Export failed list ─────────────────────────
            export_rows = []
            for s in failed_list:
                export_rows.append({
                    'Student Name':   s.get('student_name'),
                    'Student ID':     s.get('student_code'),
                    'Grade':          s.get('grade'),
                    'Section':        s.get('section'),
                    'GPA':            s.get('gpa'),
                    'Total Marks':    s.get('total_marks'),
                    'Failed Subjects':s.get('failed_subjects'),
                    'Math':           s.get('math_score'),
                    'Science':        s.get('science_score'),
                    'English':        s.get('english_score'),
                    'Social':         s.get('social_score'),
                    'Language':       s.get('language_score'),
                    'Parent Email':   s.get('parent_email'),
                    'Semester':       s.get('semester'),
                    'Exam Type':      s.get('exam_type')
                })

            export_df  = pd.DataFrame(export_rows)
            export_csv = export_df.to_csv(index=False).encode('utf-8')

            st.download_button(
                label="📥 Export Failed Students Report as CSV",
                data=export_csv,
                file_name=(
                    f"failed_students_"
                    f"{'grade' + str(fail_grade) if fail_grade != 'All Grades' else 'all'}_"
                    f"{date.today().isoformat()}.csv"
                ),
                mime="text/csv",
                use_container_width=True
            )
