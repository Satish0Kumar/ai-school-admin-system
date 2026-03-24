"""
Advanced Analytics Dashboard
ScholarSense - AI-Powered Academic Intelligence System
Enhancement 10: School-wide executive analytics & insights
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from frontend.utils.session_manager import SessionManager



# ============================================
# PAGE CONFIG
# ============================================
st.set_page_config(
    page_title="Analytics - ScholarSense",
    page_icon="📈",
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
    .main { background-color: #f0f4f8; padding: 1rem 2rem; }

    .kpi-card {
        background: white;
        padding: 1.4rem 1.2rem;
        border-radius: 16px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 14px rgba(0,0,0,0.06);
        text-align: center;
        margin-bottom: 1rem;
        transition: transform 0.2s;
    }
    .kpi-card:hover { transform: translateY(-2px); }
    .kpi-value {
        font-size: 2.4rem; font-weight: 900;
        margin: 0.3rem 0; line-height: 1.1;
    }
    .kpi-label {
        font-size: 0.78rem; color: #4a5568;
        font-weight: 700; text-transform: uppercase;
        letter-spacing: 0.06em;
    }
    .kpi-sub {
        font-size: 0.78rem; color: #718096;
        margin-top: 0.3rem;
    }
    .section-header {
        color: #1a202c; font-size: 1.25rem;
        font-weight: 800; margin: 1.5rem 0 1rem 0;
        padding-bottom: 0.4rem;
        border-bottom: 3px solid #2563eb;
        display: inline-block;
    }
    .insight-box {
        background: white; padding: 1.2rem 1.5rem;
        border-radius: 12px; border: 1px solid #e2e8f0;
        border-left: 5px solid #2563eb;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        margin-bottom: 1rem;
    }
    .insight-box.warning {
        border-left-color: #FF4B4B;
        background: #fff8f8;
    }
    .insight-box.success {
        border-left-color: #00CC44;
        background: #f0fff4;
    }
    .chart-card {
        background: white; padding: 1.2rem;
        border-radius: 14px; border: 1px solid #e2e8f0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
    }
    [data-testid="stSidebar"] {
        background-color: white;
        border-right: 1px solid #e2e8f0;
    }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ============================================
# CONSTANTS
# ============================================
API_BASE = "http://localhost:5000/api"

RISK_COLORS = {
    'Low':      '#00CC44',
    'Medium':   '#FFA500',
    'High':     '#FF4B4B',
    'Critical': '#8B0000'
}

GRADE_COLORS = [
    '#2563eb', '#00CC44', '#FFA500',
    '#FF4B4B', '#9333ea'
]

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
            timeout=20
        )
        return r.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}


@st.cache_data(ttl=600)
def cached_overview(_token):
    return api_get("/analytics/school-overview")

@st.cache_data(ttl=600)
def cached_trends(_token, months=6):
    return api_get("/analytics/trends", params={"months": months})

@st.cache_data(ttl=300)
def cached_comm_stats(_token):
    return api_get("/communications/stats")



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
    if st.button("📊 Dashboard",          width='stretch'):
        st.switch_page("pages/1_📊_Dashboard.py")
    if st.button("👥 Students",           width='stretch'):
        st.switch_page("pages/2_👥_Students.py")
    if st.button("🔁 Batch Analysis",     width='stretch'):
        st.switch_page("pages/10_🔁_Batch_Analysis.py")
    if st.button("📧 Parent Portal",      width='stretch'):
        st.switch_page("pages/11_📧_Parent_Portal.py")
    if st.button("📝 Marks Entry",        width='stretch'):
        st.switch_page("pages/9_📝_Marks_Entry.py")
    st.markdown("---")

    # Trend period selector (global)
    trend_months = st.selectbox(
        "📅 Trend Period",
        options=[3, 6, 12],
        index=1,
        format_func=lambda x: f"Last {x} months"
    )

    st.markdown("---")
    if st.button("🔄 Refresh All Data",
                 width='stretch', type="primary"):
        st.rerun()
    # REPLACE WITH:
    if st.button("🚪 Logout", width='stretch', key="analytics_logout_btn"):
        SessionManager.logout()
        st.switch_page("app.py")

# ============================================
# PAGE HEADER
# ============================================
st.markdown(f"""
    <h1 style='color:#1a202c; margin-bottom:0;'>
        📈 Advanced Analytics Dashboard
    </h1>
    <p style='color:#4a5568; margin-top:0.25rem;'>
        School-wide executive insights — All data as of
        {datetime.now().strftime('%d %b %Y, %I:%M %p')}
    </p>
    <hr style='border:none; border-top:1px solid #e2e8f0;
               margin:1rem 0;'/>
""", unsafe_allow_html=True)

# ============================================
# FETCH ALL DATA UPFRONT
# ============================================
_token = st.session_state.get('token', '')

with st.spinner("📊 Loading school analytics..."):
    overview_res = cached_overview(_token)
    trends_res   = cached_trends(_token, trend_months)
    comm_stats   = cached_comm_stats(_token)
    batch_sum    = api_get("/batch/summary")   # small call, no cache needed


# Check data loaded
if overview_res.get('status') != 'success':
    st.error(
        f"❌ Could not load analytics: "
        f"{overview_res.get('message', 'API error')}"
    )
    st.stop()

overview = overview_res['data']
trends   = trends_res.get('data', {}) \
           if trends_res.get('status') == 'success' else {}

# ============================================
# TABS
# ============================================
tab1, tab2, tab3, tab4 = st.tabs([
    "🏫 School Overview",
    "📊 Grade & GPA Analysis",
    "🎯 Risk & ML Insights",
    "📅 Trends & Activity"
])


# ============================================================
# TAB 1 — SCHOOL OVERVIEW
# ============================================================
with tab1:

    # ── Row 1: Core KPIs ──────────────────────────────────
    st.markdown(
        '<p class="section-header">🏫 School-Wide KPIs</p>',
        unsafe_allow_html=True
    )

    k1, k2, k3, k4, k5, k6 = st.columns(6)

    with k1:
        st.markdown(f"""
        <div class="kpi-card" style="border-top:5px solid #2563eb;">
            <p class="kpi-label">👥 Total Students</p>
            <p class="kpi-value" style="color:#2563eb;">
                {overview['total_active']}
            </p>
            <p class="kpi-sub">Active enrolled</p>
        </div>
        """, unsafe_allow_html=True)

    with k2:
        gpa_color = (
            '#00CC44' if overview['avg_gpa'] >= 60
            else '#FFA500' if overview['avg_gpa'] >= 45
            else '#FF4B4B'
        )
        st.markdown(f"""
        <div class="kpi-card" style="border-top:5px solid {gpa_color};">
            <p class="kpi-label">📊 School Avg GPA</p>
            <p class="kpi-value" style="color:{gpa_color};">
                {overview['avg_gpa']}%
            </p>
            <p class="kpi-sub">All grades combined</p>
        </div>
        """, unsafe_allow_html=True)

    with k3:
        att_color = (
            '#00CC44' if overview['avg_attendance'] >= 85
            else '#FFA500' if overview['avg_attendance'] >= 70
            else '#FF4B4B'
        )
        st.markdown(f"""
        <div class="kpi-card" style="border-top:5px solid {att_color};">
            <p class="kpi-label">🗓️ Avg Attendance</p>
            <p class="kpi-value" style="color:{att_color};">
                {overview['avg_attendance']}%
            </p>
            <p class="kpi-sub">School-wide rate</p>
        </div>
        """, unsafe_allow_html=True)

    with k4:
        critical = overview['risk_distribution'].get('Critical', 0)
        high     = overview['risk_distribution'].get('High', 0)
        at_risk  = critical + high
        st.markdown(f"""
        <div class="kpi-card" style="border-top:5px solid #FF4B4B;">
            <p class="kpi-label">🚨 At-Risk Students</p>
            <p class="kpi-value" style="color:#FF4B4B;">{at_risk}</p>
            <p class="kpi-sub">
                {critical} Critical · {high} High
            </p>
        </div>
        """, unsafe_allow_html=True)

    with k5:
        st.markdown(f"""
        <div class="kpi-card" style="border-top:5px solid #9333ea;">
            <p class="kpi-label">🧠 Incidents Logged</p>
            <p class="kpi-value" style="color:#9333ea;">
                {overview['total_incidents']}
            </p>
            <p class="kpi-sub">Behavioral records</p>
        </div>
        """, unsafe_allow_html=True)

    with k6:
        st.markdown(f"""
        <div class="kpi-card" style="border-top:5px solid #0891b2;">
            <p class="kpi-label">📧 Emails Sent</p>
            <p class="kpi-value" style="color:#0891b2;">
                {overview['total_communications']}
            </p>
            <p class="kpi-sub">Parent contacts</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Row 2: Smart Insights ──────────────────────────────
    st.markdown(
        '<p class="section-header">💡 Smart Insights</p>',
        unsafe_allow_html=True
    )

    risk_dist    = overview['risk_distribution']
    total_pred   = overview['total_predictions']
    total_active = overview['total_active']

    # Generate dynamic insights
    insights = []

    # Insight 1: At-risk percentage
    if total_pred > 0:
        at_risk_pct = round((at_risk / total_pred) * 100, 1)
        if at_risk_pct >= 30:
            insights.append(('warning',
                f"🚨 **{at_risk_pct}%** of predicted students are at "
                f"High or Critical risk ({at_risk} students). "
                f"Immediate intervention recommended."
            ))
        elif at_risk_pct >= 15:
            insights.append(('warning',
                f"⚠️ **{at_risk_pct}%** of predicted students are at "
                f"High or Critical risk ({at_risk} students). "
                f"Consider batch parent notification."
            ))
        else:
            insights.append(('success',
                f"✅ Only **{at_risk_pct}%** of students are at "
                f"High or Critical risk. School performance is healthy!"
            ))

    # Insight 2: GPA health
    if overview['avg_gpa'] < 45:
        insights.append(('warning',
            f"📉 School average GPA is **{overview['avg_gpa']}%** — "
            f"below the pass threshold. Review marks and teaching quality."
        ))
    elif overview['avg_gpa'] >= 70:
        insights.append(('success',
            f"🏆 Excellent school average GPA of "
            f"**{overview['avg_gpa']}%**!"
        ))

    # Insight 3: Attendance
    if overview['avg_attendance'] < 75:
        insights.append(('warning',
            f"🗓️ Average attendance is only "
            f"**{overview['avg_attendance']}%** — "
            f"send Attendance Alerts to parents via Parent Portal."
        ))

    # Insight 4: Unpredicted students
    unpred = total_active - total_pred
    if unpred > 0:
        insights.append(('info',
            f"ℹ️ **{unpred}** students have no ML prediction yet. "
            f"Run Batch Analysis to generate predictions."
        ))

    # Insight 5: Grade performance leader
    grade_stats = overview.get('grade_stats', [])
    if grade_stats:
        best_grade  = max(grade_stats, key=lambda x: x['avg_gpa'])
        worst_grade = min(grade_stats, key=lambda x: x['avg_gpa'])
        insights.append(('success',
            f"🏆 **Grade {best_grade['grade']}** leads with avg GPA "
            f"**{best_grade['avg_gpa']}%** | "
            f"Grade {worst_grade['grade']} needs attention "
            f"({worst_grade['avg_gpa']}%)"
        ))

    # Render insights
    for ins_type, ins_text in insights:
        css_class = (
            'insight-box warning' if ins_type == 'warning'
            else 'insight-box success' if ins_type == 'success'
            else 'insight-box'
        )
        st.markdown(
            f'<div class="{css_class}">{ins_text}</div>',
            unsafe_allow_html=True
        )

    st.markdown("---")

    # ── Row 3: Risk Donut + Grade Breakdown ───────────────
    st.markdown(
        '<p class="section-header">📊 School Composition</p>',
        unsafe_allow_html=True
    )

    rc1, rc2, rc3 = st.columns([1, 1, 1])

    # Risk distribution donut
    with rc1:
        risk_labels = [k for k, v in risk_dist.items() if v > 0]
        risk_values = [v for v in risk_dist.values() if v > 0]
        risk_clrs   = [RISK_COLORS.get(l, '#ccc') for l in risk_labels]

        if risk_values:
            fig_risk = go.Figure(data=[go.Pie(
                labels=risk_labels,
                values=risk_values,
                marker=dict(colors=risk_clrs),
                hole=0.5,
                textinfo='label+value',
                textfont=dict(size=11),
                hovertemplate=(
                    '<b>%{label}</b><br>'
                    'Students: %{value}<br>'
                    '%{percent}<extra></extra>'
                )
            )])
            fig_risk.update_layout(
                **get_plotly_layout("🎯 Risk Distribution", height=300, margin=dict(t=45, b=10, l=10, r=10), legend=dict(orientation='h', x=0.1, y=-0.15, font=dict(size=10))),
                showlegend=True
            )
            st.plotly_chart(fig_risk, width='stretch')
        else:
            st.info("ℹ️ No risk predictions yet.")

    # Students per grade bar
    with rc2:
        if grade_stats:
            g_labels = [f"Grade {g['grade']}" for g in grade_stats]
            g_values = [g['total']             for g in grade_stats]

            fig_grade_count = go.Figure(data=[go.Bar(
                x=g_labels,
                y=g_values,
                marker_color=GRADE_COLORS[:len(g_labels)],
                text=g_values,
                textposition='outside',
                width=0.5
            )])
            fig_grade_count.update_layout(
                **get_plotly_layout("👥 Students per Grade", height=300, margin=dict(t=45, b=40, l=40, r=20), xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, rangemode='tozero')),
                showlegend=False
            )
            st.plotly_chart(fig_grade_count, width='stretch')

    # Module activity donut
    with rc3:
        act_labels = [
            'Students', 'Predictions',
            'Incidents', 'Communications'
        ]
        act_values = [
            overview['total_active'],
            overview['total_predictions'],
            overview['total_incidents'],
            overview['total_communications']
        ]
        act_colors = ['#2563eb', '#9333ea', '#FFA500', '#0891b2']

        fig_act = go.Figure(data=[go.Pie(
            labels=act_labels,
            values=act_values,
            marker=dict(colors=act_colors),
            hole=0.5,
            textinfo='label+value',
            textfont=dict(size=11),
            hovertemplate=(
                '<b>%{label}</b><br>'
                'Count: %{value}<extra></extra>'
            )
        )])
        fig_act.update_layout(
            **get_plotly_layout("🔢 Module Activity", height=300, margin=dict(t=45, b=10, l=10, r=10), legend=dict(orientation='h', x=0.0, y=-0.15, font=dict(size=10))),
            showlegend=True
        )
        st.plotly_chart(fig_act, width='stretch')


# ============================================================
# TAB 2 — GRADE & GPA ANALYSIS
# ============================================================
with tab2:
    st.markdown("### 📊 Grade & GPA Analysis")
    st.markdown("---")

    grade_stats   = overview.get('grade_stats', [])
    section_stats = overview.get('section_stats', [])
    gpa_by_grade  = trends.get('gpa_by_grade', [])

    if not grade_stats:
        st.info(
            "ℹ️ No grade data available yet. "
            "Add academic records to see analysis."
        )
    else:
        # ── GPA by Grade bar chart ─────────────────────────
        st.markdown(
            '<p class="section-header">📈 Average GPA per Grade</p>',
            unsafe_allow_html=True
        )

        ga1, ga2 = st.columns(2)

        with ga1:
            g_names  = [f"Grade {g['grade']}" for g in grade_stats]
            g_gpas   = [g['avg_gpa']           for g in grade_stats]
            g_colors = [
                '#00CC44' if v >= 60
                else '#FFA500' if v >= 45
                else '#FF4B4B'
                for v in g_gpas
            ]

            fig_gpa = go.Figure(data=[go.Bar(
                x=g_names,
                y=g_gpas,
                marker_color=g_colors,
                text=[f"{v}%" for v in g_gpas],
                textposition='outside',
                width=0.5,
                hovertemplate=(
                    '<b>%{x}</b><br>'
                    'Avg GPA: %{y}%<extra></extra>'
                )
            )])
            fig_gpa.add_hline(
                y=35, line_dash="dash",
                line_color="#FF4B4B",
                annotation_text="Pass Mark (35%)",
                annotation_position="top right"
            )
            fig_gpa.add_hline(
                y=60, line_dash="dot",
                line_color="#00CC44",
                annotation_text="Good (60%)",
                annotation_position="top right"
            )
            fig_gpa.update_layout(
                **get_plotly_layout("📊 Grade-wise Average GPA", height=360, margin=dict(t=50, b=40, l=50, r=20), xaxis=dict(showgrid=False), yaxis=dict(title='Average GPA (%)', range=[0, 110], showgrid=True))
            )
            st.plotly_chart(fig_gpa, width='stretch')

        # GPA min/max/avg range chart
        with ga2:
            if gpa_by_grade:
                fig_range = go.Figure()

                grades_r  = [f"Grade {g['grade']}" for g in gpa_by_grade]
                avg_gpas  = [g['avg_gpa']           for g in gpa_by_grade]
                min_gpas  = [g['min_gpa']           for g in gpa_by_grade]
                max_gpas  = [g['max_gpa']           for g in gpa_by_grade]

                # Range band
                fig_range.add_trace(go.Scatter(
                    x=grades_r + grades_r[::-1],
                    y=max_gpas + min_gpas[::-1],
                    fill='toself',
                    fillcolor='rgba(37,99,235,0.1)',
                    line=dict(color='rgba(255,255,255,0)'),
                    name='GPA Range',
                    hoverinfo='skip'
                ))

                # Avg line
                fig_range.add_trace(go.Scatter(
                    x=grades_r,
                    y=avg_gpas,
                    mode='lines+markers+text',
                    name='Avg GPA',
                    line=dict(color='#2563eb', width=3),
                    marker=dict(size=9, color='#2563eb'),
                    text=[f"{v}%" for v in avg_gpas],
                    textposition='top center',
                    textfont=dict(size=11),
                    hovertemplate=(
                        '<b>%{x}</b><br>'
                        'Avg: %{y}%<extra></extra>'
                    )
                ))

                fig_range.update_layout(
                    **get_plotly_layout("📉 GPA Range (Min / Avg / Max)", height=360, margin=dict(t=50, b=50, l=50, r=20), legend=dict(orientation='h', x=0, y=-0.2), xaxis=dict(title='Grade', showgrid=False), yaxis=dict(title='GPA (%)', range=[0, 105], showgrid=True))
                )
                st.plotly_chart(fig_range, width='stretch')

        st.markdown("---")

        # ── Risk Heatmap: Grade × Section ─────────────────
        st.markdown(
            '<p class="section-header">'
            '🔥 Risk Heatmap — Grade × Section'
            '</p>',
            unsafe_allow_html=True
        )

        if section_stats:
            # Pivot for heatmap
            sec_df = pd.DataFrame(section_stats)

            grades   = sorted(sec_df['grade'].unique())
            sections = sorted(sec_df['section'].unique())

            # Build GPA matrix
            gpa_matrix  = []
            risk_matrix = []
            text_matrix = []

            for g in grades:
                gpa_row  = []
                risk_row = []
                text_row = []
                for s in sections:
                    row = sec_df[
                        (sec_df['grade'] == g) &
                        (sec_df['section'] == s)
                    ]
                    if not row.empty:
                        gpa  = float(row.iloc[0]['avg_gpa'])
                        risk = int(row.iloc[0]['at_risk_count'])
                        tot  = int(row.iloc[0]['total'])
                    else:
                        gpa  = 0.0
                        risk = 0
                        tot  = 0

                    gpa_row.append(gpa)
                    risk_row.append(risk)
                    text_row.append(
                        f"GPA: {gpa}%<br>"
                        f"At-Risk: {risk}<br>"
                        f"Total: {tot}"
                        if tot > 0 else "No Data"
                    )

                gpa_matrix.append(gpa_row)
                text_matrix.append(text_row)

            hm1, hm2 = st.columns(2)

            with hm1:
                fig_heatmap = go.Figure(data=go.Heatmap(
                    z=gpa_matrix,
                    x=[f"Section {s}" for s in sections],
                    y=[f"Grade {g}"   for g in grades],
                    text=text_matrix,
                    hovertemplate=(
                        '<b>%{y} %{x}</b><br>'
                        '%{text}<extra></extra>'
                    ),
                    colorscale=[
                        [0.0,  '#FF4B4B'],
                        [0.35, '#FFA500'],
                        [0.6,  '#FFD700'],
                        [0.8,  '#90EE90'],
                        [1.0,  '#00CC44']
                    ],
                    colorbar=dict(
                        title='GPA %',
                        tickfont=dict(size=10)
                    ),
                    zmin=0,
                    zmax=100
                ))
                fig_heatmap.update_layout(
                    **get_plotly_layout("🔥 GPA Heatmap (Grade × Section)", height=350, margin=dict(t=50, b=40, l=70, r=20), xaxis=dict(side='bottom'))
                )
                st.plotly_chart(fig_heatmap, width='stretch')

            with hm2:
                # Grade stats summary table
                st.markdown("**📋 Grade Summary Table**")
                sum_rows = []
                for g in grade_stats:
                    gpa_val = g['avg_gpa']
                    health  = (
                        '🟢 Good'   if gpa_val >= 60
                        else '🟠 Average' if gpa_val >= 45
                        else '🔴 Poor'
                    )
                    sum_rows.append({
                        'Grade':    f"Grade {g['grade']}",
                        'Students': g['total'],
                        'Avg GPA':  f"{gpa_val}%",
                        'Status':   health
                    })
                sum_df = pd.DataFrame(sum_rows)
                st.dataframe(
                    sum_df,
                    width='stretch',
                    hide_index=True,
                    height=280
                )

                # Top performing section
                if section_stats:
                    best_sec = max(
                        section_stats,
                        key=lambda x: x['avg_gpa']
                    )
                    st.markdown(f"""
                    <div class="insight-box success">
                        🏆 <b>Best Performing:</b>
                        Grade {best_sec['grade']} Section {best_sec['section']}
                        — Avg GPA <b>{best_sec['avg_gpa']}%</b>
                    </div>
                    """, unsafe_allow_html=True)


# ============================================================
# TAB 3 — RISK & ML INSIGHTS
# ============================================================
with tab3:
    st.markdown("### 🎯 Risk & ML Insights")
    st.markdown("---")

    risk_dist   = overview.get('risk_distribution', {})
    conf_dist   = overview.get('confidence_distribution', {})
    total_pred  = overview.get('total_predictions', 0)
    total_act   = overview.get('total_active', 0)
    total_unpred= total_act - total_pred

    # ── KPI Row ────────────────────────────────────────────
    st.markdown(
        '<p class="section-header">🤖 ML Prediction Summary</p>',
        unsafe_allow_html=True
    )

    ml1, ml2, ml3, ml4, ml5 = st.columns(5)

    with ml1:
        st.markdown(f"""
        <div class="kpi-card" style="border-top:5px solid #2563eb;">
            <p class="kpi-label">🤖 Predictions Run</p>
            <p class="kpi-value" style="color:#2563eb;">
                {total_pred}
            </p>
            <p class="kpi-sub">Students analysed</p>
        </div>
        """, unsafe_allow_html=True)

    with ml2:
        coverage = round((total_pred / total_act) * 100, 1) \
                   if total_act > 0 else 0
        cov_color = (
            '#00CC44' if coverage >= 90
            else '#FFA500' if coverage >= 70
            else '#FF4B4B'
        )
        st.markdown(f"""
        <div class="kpi-card" style="border-top:5px solid {cov_color};">
            <p class="kpi-label">📊 Coverage</p>
            <p class="kpi-value" style="color:{cov_color};">
                {coverage}%
            </p>
            <p class="kpi-sub">of active students</p>
        </div>
        """, unsafe_allow_html=True)

    with ml3:
        st.markdown(f"""
        <div class="kpi-card" style="border-top:5px solid #FFA500;">
            <p class="kpi-label">⏳ Not Yet Predicted</p>
            <p class="kpi-value" style="color:#FFA500;">
                {total_unpred}
            </p>
            <p class="kpi-sub">Need batch run</p>
        </div>
        """, unsafe_allow_html=True)

    with ml4:
        critical = risk_dist.get('Critical', 0)
        st.markdown(f"""
        <div class="kpi-card" style="border-top:5px solid #8B0000;">
            <p class="kpi-label">🚨 Critical Risk</p>
            <p class="kpi-value" style="color:#8B0000;">
                {critical}
            </p>
            <p class="kpi-sub">Urgent attention</p>
        </div>
        """, unsafe_allow_html=True)

    with ml5:
        low = risk_dist.get('Low', 0)
        st.markdown(f"""
        <div class="kpi-card" style="border-top:5px solid #00CC44;">
            <p class="kpi-label">🟢 Low Risk</p>
            <p class="kpi-value" style="color:#00CC44;">
                {low}
            </p>
            <p class="kpi-sub">Performing well</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Row 2: Risk Funnel + Confidence Chart ──────────────
    st.markdown(
        '<p class="section-header">'
        '📉 Dropout Risk Funnel & Confidence'
        '</p>',
        unsafe_allow_html=True
    )

    rf1, rf2 = st.columns(2)

    # Dropout risk funnel
    with rf1:
        funnel_stages  = ['Low Risk', 'Medium Risk',
                          'High Risk', 'Critical Risk']
        funnel_values  = [
            risk_dist.get('Low',      0),
            risk_dist.get('Medium',   0),
            risk_dist.get('High',     0),
            risk_dist.get('Critical', 0)
        ]
        funnel_colors  = ['#00CC44', '#FFA500', '#FF4B4B', '#8B0000']

        if any(v > 0 for v in funnel_values):
            fig_funnel = go.Figure(go.Funnel(
                y=funnel_stages,
                x=funnel_values,
                textinfo='value+percent initial',
                marker=dict(color=funnel_colors),
                connector=dict(
                    line=dict(color='#e2e8f0', width=2)
                ),
                hovertemplate=(
                    '<b>%{y}</b><br>'
                    'Students: %{x}<br>'
                    '%{percentInitial}<extra></extra>'
                )
            ))
            fig_funnel.update_layout(
                **get_plotly_layout("📉 Dropout Risk Funnel", height=380, margin=dict(t=50, b=20, l=120, r=40))
            )
            st.plotly_chart(fig_funnel, width='stretch')
        else:
            st.info(
                "ℹ️ No risk data yet. "
                "Run batch predictions first."
            )

    # Confidence distribution bar
    with rf2:
        if conf_dist and any(v > 0 for v in conf_dist.values()):
            conf_labels = list(conf_dist.keys())
            conf_values = list(conf_dist.values())
            conf_colors = ['#2563eb', '#00CC44', '#FFA500', '#FF4B4B']

            fig_conf = go.Figure(data=[go.Bar(
                x=conf_labels,
                y=conf_values,
                marker_color=conf_colors,
                text=conf_values,
                textposition='outside',
                width=0.5,
                hovertemplate=(
                    '<b>%{x}</b><br>'
                    'Students: %{y}<extra></extra>'
                )
            )])
            fig_conf.update_layout(
                **get_plotly_layout("🎯 ML Confidence Distribution", height=380, margin=dict(t=50, b=50, l=50, r=20), xaxis=dict(title='Confidence Band', showgrid=False), yaxis=dict(title='Number of Students', showgrid=True, rangemode='tozero'))
            )
            st.plotly_chart(fig_conf, width='stretch')

            # Confidence insight
            high_conf = conf_dist.get('90-100%', 0)
            total_conf_students = sum(conf_dist.values())
            if total_conf_students > 0:
                high_conf_pct = round(
                    (high_conf / total_conf_students) * 100, 1
                )
                st.markdown(f"""
                <div class="insight-box success">
                    🎯 <b>{high_conf_pct}%</b> of predictions have
                    <b>90%+ confidence</b> — the ML model is
                    highly reliable for {high_conf} students.
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info(
                "ℹ️ No confidence data available. "
                "Run batch predictions to populate."
            )

    st.markdown("---")

    # ── Row 3: Risk × Grade Stacked Bar ───────────────────
    st.markdown(
        '<p class="section-header">'
        '📊 Risk Distribution by Grade'
        '</p>',
        unsafe_allow_html=True
    )

    # Fetch per-grade risk breakdown
    with st.spinner("Loading grade risk breakdown..."):
        grade_risk_data = {}
        for grade in [6, 7, 8, 9, 10]:
            res = api_get(
                "/batch/predictions",
                params={"grade": grade, "limit": 500}
            )
            if res.get('status') == 'success':
                students = res['data'].get('students', [])
                counts   = {'Low': 0, 'Medium': 0,
                            'High': 0, 'Critical': 0}
                for s in students:
                    lbl = s.get('risk_label', 'Low')
                    if lbl in counts:
                        counts[lbl] += 1
                if any(v > 0 for v in counts.values()):
                    grade_risk_data[grade] = counts

    if grade_risk_data:
        gb1, gb2 = st.columns([2, 1])

        with gb1:
            grade_labels = [
                f"Grade {g}" for g in grade_risk_data.keys()
            ]
            fig_stacked  = go.Figure()

            for risk_level, color in RISK_COLORS.items():
                fig_stacked.add_trace(go.Bar(
                    name=risk_level,
                    x=grade_labels,
                    y=[
                        grade_risk_data[g].get(risk_level, 0)
                        for g in grade_risk_data.keys()
                    ],
                    marker_color=color,
                    hovertemplate=(
                        f'<b>{risk_level}</b><br>'
                        '%{x}: %{y} students<extra></extra>'
                    )
                ))

            fig_stacked.update_layout(
                **get_plotly_layout("📊 Risk Breakdown by Grade", height=360, margin=dict(t=50, b=60, l=50, r=20), legend=dict(orientation='h', x=0, y=-0.25), xaxis=dict(showgrid=False), yaxis=dict(title='Students', showgrid=True)),
                barmode='stack'
            )
            st.plotly_chart(fig_stacked, width='stretch')

        with gb2:
            st.markdown("**🔢 Grade Risk Table**")
            grade_risk_rows = []
            for g, counts in grade_risk_data.items():
                total_g   = sum(counts.values())
                at_risk_g = counts.get('High', 0) + \
                            counts.get('Critical', 0)
                grade_risk_rows.append({
                    'Grade':    f"Grade {g}",
                    '🟢 Low':   counts.get('Low', 0),
                    '🟠 Med':   counts.get('Medium', 0),
                    '🔴 High':  counts.get('High', 0),
                    '🚨 Crit':  counts.get('Critical', 0),
                    'At-Risk':  at_risk_g,
                    'Total':    total_g
                })
            gr_df = pd.DataFrame(grade_risk_rows)
            st.dataframe(
                gr_df,
                width='stretch',
                hide_index=True,
                height=280
            )
    else:
        st.info(
            "ℹ️ No prediction data per grade yet. "
            "Run batch predictions."
        )


# ============================================================
# TAB 4 — TRENDS & ACTIVITY + EXPORT
# ============================================================
with tab4:
    st.markdown("### 📅 Trends & Activity")
    st.markdown(
        f"Showing last **{trend_months} months** "
        f"(change in sidebar)"
    )
    st.markdown("---")

    incident_trends = trends.get('incident_trends', [])
    comm_trends     = trends.get('comm_trends', [])

    # ── Row 1: Incident + Communication Trends ─────────────
    st.markdown(
        '<p class="section-header">📈 Activity Over Time</p>',
        unsafe_allow_html=True
    )

    tr1, tr2 = st.columns(2)

    # Behavioral incident trend
    with tr1:
        if incident_trends:
            inc_months = [t['month'] for t in incident_trends]
            inc_counts = [t['count'] for t in incident_trends]

            fig_inc = go.Figure()
            fig_inc.add_trace(go.Scatter(
                x=inc_months,
                y=inc_counts,
                mode='lines+markers+text',
                name='Incidents',
                line=dict(color='#9333ea', width=3),
                marker=dict(size=9, color='#9333ea'),
                fill='tozeroy',
                fillcolor='rgba(147,51,234,0.1)',
                text=inc_counts,
                textposition='top center',
                textfont=dict(size=10),
                hovertemplate=(
                    '<b>%{x}</b><br>'
                    'Incidents: %{y}<extra></extra>'
                )
            ))
            fig_inc.update_layout(
                **get_plotly_layout("🧠 Behavioral Incidents per Month", height=320, margin=dict(t=50, b=50, l=50, r=20), xaxis=dict(title='Month', showgrid=False), yaxis=dict(title='Incident Count', showgrid=True, rangemode='tozero')),
                showlegend=False
            )
            st.plotly_chart(fig_inc, width='stretch')
        else:
            st.info(
                "ℹ️ No incident trend data yet. "
                "Log behavioral incidents to see trends."
            )

    # Communication trend
    with tr2:
        if comm_trends:
            cm_months = [t['month'] for t in comm_trends]
            cm_counts = [t['count'] for t in comm_trends]

            fig_comm = go.Figure()
            fig_comm.add_trace(go.Scatter(
                x=cm_months,
                y=cm_counts,
                mode='lines+markers+text',
                name='Emails',
                line=dict(color='#0891b2', width=3),
                marker=dict(size=9, color='#0891b2'),
                fill='tozeroy',
                fillcolor='rgba(8,145,178,0.1)',
                text=cm_counts,
                textposition='top center',
                textfont=dict(size=10),
                hovertemplate=(
                    '<b>%{x}</b><br>'
                    'Emails Sent: %{y}<extra></extra>'
                )
            ))
            fig_comm.update_layout(
                **get_plotly_layout("📧 Parent Emails Sent per Month", height=320, margin=dict(t=50, b=50, l=50, r=20), xaxis=dict(title='Month', showgrid=False), yaxis=dict(title='Emails Sent', showgrid=True, rangemode='tozero')),
                showlegend=False
            )
            st.plotly_chart(fig_comm, width='stretch')
        else:
            st.info(
                "ℹ️ No email trend data yet. "
                "Send parent emails to see trends."
            )

    st.markdown("---")

    # ── Row 2: Communication by type + Top Classes ─────────
    st.markdown(
        '<p class="section-header">'
        '🏆 Top Classes & Communication Breakdown'
        '</p>',
        unsafe_allow_html=True
    )

    tc1, tc2 = st.columns(2)

    # Top performing classes table
    with tc1:
        st.markdown("**🏆 Top Performing Classes (by Avg GPA)**")
        section_stats = overview.get('section_stats', [])

        if section_stats:
            top_classes = sorted(
                [s for s in section_stats if s['avg_gpa'] > 0],
                key=lambda x: x['avg_gpa'],
                reverse=True
            )[:10]

            top_rows = []
            for rank, cls in enumerate(top_classes, 1):
                medal = {1: '🥇', 2: '🥈', 3: '🥉'}.get(rank, f'#{rank}')
                top_rows.append({
                    'Rank':      medal,
                    'Class':     f"Grade {cls['grade']} "
                                 f"Sec {cls['section']}",
                    'Students':  cls['total'],
                    'Avg GPA':   f"{cls['avg_gpa']}%",
                    'At-Risk':   cls['at_risk_count']
                })
            top_df = pd.DataFrame(top_rows)
            st.dataframe(
                top_df,
                width='stretch',
                hide_index=True,
                height=300
            )
        else:
            st.info("ℹ️ No class data available yet.")

    # Communication by type horizontal bar
    with tc2:
        st.markdown("**📧 Emails by Communication Type**")
        if comm_stats.get('status') == 'success':
            by_type = comm_stats['data'].get('by_type', [])
            if by_type:
                type_labels = [x['type']  for x in by_type]
                type_values = [x['count'] for x in by_type]
                type_colors = [
                    '#2563eb', '#00CC44', '#FFA500',
                    '#FF4B4B', '#9333ea', '#0891b2', '#e377c2'
                ]

                fig_ctype = go.Figure(data=[go.Bar(
                    y=type_labels,
                    x=type_values,
                    orientation='h',
                    marker_color=type_colors[:len(type_labels)],
                    text=type_values,
                    textposition='outside',
                    hovertemplate=(
                        '<b>%{y}</b><br>'
                        'Sent: %{x}<extra></extra>'
                    )
                )])
                fig_ctype.update_layout(
                    **get_plotly_layout(height=300, margin=dict(t=10, b=40, l=140, r=40), xaxis=dict(title='Emails Sent', showgrid=True, rangemode='tozero'), yaxis=dict(showgrid=False))
                )
                st.plotly_chart(fig_ctype, width='stretch')
            else:
                st.info("ℹ️ No emails sent yet.")

    st.markdown("---")

    # ── Full School Report Export ──────────────────────────
    st.markdown(
        '<p class="section-header">📥 Full School Report Export</p>',
        unsafe_allow_html=True
    )

    st.markdown(
        "Export a comprehensive CSV report covering all modules "
        "for offline analysis or admin records."
    )

    exp1, exp2, exp3 = st.columns(3)

    # Export 1: School Overview
    with exp1:
        st.markdown("**🏫 School KPI Report**")
        kpi_rows = [
            {'Metric': 'Total Active Students',
             'Value':  overview['total_active']},
            {'Metric': 'School Average GPA (%)',
             'Value':  overview['avg_gpa']},
            {'Metric': 'Average Attendance (%)',
             'Value':  overview['avg_attendance']},
            {'Metric': 'Critical Risk Students',
             'Value':  risk_dist.get('Critical', 0)},
            {'Metric': 'High Risk Students',
             'Value':  risk_dist.get('High', 0)},
            {'Metric': 'Medium Risk Students',
             'Value':  risk_dist.get('Medium', 0)},
            {'Metric': 'Low Risk Students',
             'Value':  risk_dist.get('Low', 0)},
            {'Metric': 'Total Predictions Run',
             'Value':  overview['total_predictions']},
            {'Metric': 'Total Incidents Logged',
             'Value':  overview['total_incidents']},
            {'Metric': 'Total Emails Sent',
             'Value':  overview['total_communications']},
            {'Metric': 'Report Generated At',
             'Value':  datetime.now().strftime('%d %b %Y %I:%M %p')}
        ]
        kpi_df  = pd.DataFrame(kpi_rows)
        kpi_csv = kpi_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download KPI Report",
            data=kpi_csv,
            file_name=(
                f"school_kpi_report_"
                f"{datetime.now().strftime('%Y%m%d')}.csv"
            ),
            mime="text/csv",
            width='stretch',
            type="primary"
        )

    # Export 2: Grade-wise report
    with exp2:
        st.markdown("**📊 Grade-wise GPA Report**")
        if grade_stats:
            grade_export_rows = []
            for g in grade_stats:
                grade_export_rows.append({
                    'Grade':           g['grade'],
                    'Total Students':  g['total'],
                    'Avg GPA (%)':     g['avg_gpa'],
                    'Risk - Critical': grade_risk_data.get(
                        g['grade'], {}
                    ).get('Critical', 'N/A'),
                    'Risk - High':     grade_risk_data.get(
                        g['grade'], {}
                    ).get('High', 'N/A'),
                    'Risk - Medium':   grade_risk_data.get(
                        g['grade'], {}
                    ).get('Medium', 'N/A'),
                    'Risk - Low':      grade_risk_data.get(
                        g['grade'], {}
                    ).get('Low', 'N/A')
                })
            grade_export_df  = pd.DataFrame(grade_export_rows)
            grade_export_csv = grade_export_df.to_csv(
                index=False
            ).encode('utf-8')
            st.download_button(
                label="📥 Download Grade Report",
                data=grade_export_csv,
                file_name=(
                    f"grade_report_"
                    f"{datetime.now().strftime('%Y%m%d')}.csv"
                ),
                mime="text/csv",
                width='stretch',
                type="primary"
            )

    # Export 3: Section-wise heatmap data
    with exp3:
        st.markdown("**🔥 Section Heatmap Data**")
        if section_stats:
            sec_export_df  = pd.DataFrame(section_stats)
            sec_export_csv = sec_export_df.to_csv(
                index=False
            ).encode('utf-8')
            st.download_button(
                label="📥 Download Section Data",
                data=sec_export_csv,
                file_name=(
                    f"section_heatmap_"
                    f"{datetime.now().strftime('%Y%m%d')}.csv"
                ),
                mime="text/csv",
                width='stretch',
                type="primary"
            )

    st.markdown("---")

    # ── Footer ─────────────────────────────────────────────
    st.markdown(f"""
    <div style='background:white; padding:1.2rem 1.5rem;
                border-radius:12px; border:1px solid #e2e8f0;
                text-align:center;
                box-shadow:0 2px 8px rgba(0,0,0,0.04);'>
        <p style='margin:0; color:#2563eb; font-size:1rem;
                  font-weight:800;'>🎓 ScholarSense</p>
        <p style='margin:0.3rem 0 0 0; color:#4a5568;
                  font-size:0.85rem;'>
            AI-Powered Academic Intelligence System
            &nbsp;|&nbsp;
            Enhancement 10: Advanced Analytics Dashboard
            &nbsp;|&nbsp;
            Report generated:
            {datetime.now().strftime('%d %b %Y, %I:%M %p')}
        </p>
        <p style='margin:0.5rem 0 0 0; color:#718096;
                  font-size:0.78rem;'>
            ✅ Enhancement 4 · 5 · 6 · 8 · 9 · 10 — All Complete
        </p>
    </div>
    """, unsafe_allow_html=True)

