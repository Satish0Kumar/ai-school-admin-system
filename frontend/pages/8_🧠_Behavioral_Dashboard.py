"""
Behavioral Dashboard
ScholarSense - AI-Powered Academic Intelligence System
Enhancement 5: Behavioral Analytics Dashboard
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
from datetime import datetime, date, timedelta
from frontend.utils.session_manager import SessionManager

# ============================================
# PAGE CONFIG
# ============================================
st.set_page_config(
    page_title="Behavioral Dashboard - ScholarSense",
    page_icon="🧠",
    layout="wide"
)

from frontend.utils.sidebar import render_sidebar
render_sidebar()


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
    .kpi-card {
        background: white;
        padding: 1.5rem;
        border-radius: 14px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        text-align: center;
        margin-bottom: 1rem;
    }
    .kpi-value {
        font-size: 2.4rem;
        font-weight: 800;
        margin: 0.25rem 0;
        line-height: 1.1;
    }
    .kpi-label {
        font-size: 0.85rem;
        color: #4a5568;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }
    .kpi-sub {
        font-size: 0.8rem;
        color: #718096;
        margin-top: 0.3rem;
    }
    .section-header {
        color: #1a202c;
        font-size: 1.3rem;
        font-weight: 700;
        margin: 1.5rem 0 1rem 0;
        padding-bottom: 0.4rem;
        border-bottom: 3px solid #2563eb;
        display: inline-block;
    }
    .filter-bar {
        background: white;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        margin-bottom: 1.5rem;
    }
    [data-testid="stSidebar"] {
        background-color: white;
        border-right: 1px solid #e2e8f0;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ============================================
# CONSTANTS
# ============================================
API_BASE = "http://localhost:5000/api"

SEVERITY_COLORS = {
    'Minor':    '#00CC44',
    'Moderate': '#FFA500',
    'Serious':  '#FF4B4B',
    'Critical': '#8B0000'
}

INCIDENT_TYPES = [
    'Disciplinary', 'Disruptive', 'Bullying',
    'Academic Misconduct', 'Attendance Issue',
    'Property Damage', 'Other'
]

# ============================================
# HELPERS
# ============================================
def get_headers():
    return {"Authorization": f"Bearer {st.session_state.get('token', '')}"}

def api_get(endpoint, params=None):
    """Generic GET with error handling"""
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

def fetch_stats(date_range='30_days'):
    """Fetch incident statistics"""
    return api_get("/incidents/stats", params={"range": date_range})

def fetch_trends(days=30):
    """Fetch incident trend data"""
    return api_get("/incidents/trends", params={"days": days})

def fetch_incidents(filters=None):
    """Fetch incidents with optional filters"""
    return api_get("/incidents", params=filters or {})

def get_range_days(date_range):
    """Convert range label to days int"""
    return {
        '7_days':   7,
        '30_days':  30,
        '90_days':  90,
        'all_time': 365
    }.get(date_range, 30)

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
    if st.button("📊 Dashboard",           use_container_width=True):
        st.switch_page("pages/1_📊_Dashboard.py")
    if st.button("👥 Students",            use_container_width=True):
        st.switch_page("pages/2_👥_Students.py")
    if st.button("🎯 Predictions",         use_container_width=True):
        st.switch_page("pages/4_🎯_Predictions.py")
    if st.button("📝 Incident Logging",    use_container_width=True):
        st.switch_page("pages/6_📝_Incident_Logging.py")
    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True, type="primary"):
        SessionManager.logout()
        st.switch_page("app.py")

# ============================================
# PAGE HEADER
# ============================================
st.markdown("""
    <h1 style='color:#1a202c; margin-bottom:0;'>🧠 Behavioral Dashboard</h1>
    <p style='color:#4a5568; margin-top:0.25rem;'>
        Analytics & insights on student behavioral incidents
    </p>
    <hr style='border:none; border-top:1px solid #e2e8f0; margin:1rem 0;'/>
""", unsafe_allow_html=True)

# ============================================
# GLOBAL FILTERS BAR
# ============================================
st.markdown("#### 🔍 Filters")
with st.container():
    f1, f2, f3, f4 = st.columns([2, 2, 2, 1])

    with f1:
        date_range = st.selectbox(
            "📅 Date Range",
            options=['7_days', '30_days', '90_days', 'all_time'],
            index=1,
            format_func=lambda x: {
                '7_days':   'Last 7 Days',
                '30_days':  'Last 30 Days',
                '90_days':  'Last 90 Days',
                'all_time': 'All Time'
            }[x]
        )
    with f2:
        grade_filter = st.selectbox(
            "🎓 Grade",
            options=['All Grades', 6, 7, 8, 9, 10]
        )
    with f3:
        type_filter = st.selectbox(
            "📌 Incident Type",
            options=['All Types'] + INCIDENT_TYPES
        )
    with f4:
        st.markdown("<br/>", unsafe_allow_html=True)
        refresh_btn = st.button("🔄 Refresh", use_container_width=True)

st.markdown("---")

# ============================================
# FETCH DATA
# ============================================
days = get_range_days(date_range)

with st.spinner("📊 Loading behavioral analytics..."):
    stats_result  = fetch_stats(date_range)
    trends_result = fetch_trends(days)

    # Build incident fetch params
    inc_params = {"limit": 500, "date_from": (date.today() - timedelta(days=days)).isoformat()}
    if grade_filter != 'All Grades':
        inc_params['grade'] = grade_filter
    if type_filter != 'All Types':
        inc_params['type'] = type_filter

    incidents_result = fetch_incidents(inc_params)

# Extract data safely
stats     = stats_result.get('data', {})     if stats_result.get('status')    == 'success' else {}
trends    = trends_result.get('data', {})    if trends_result.get('status')   == 'success' else {}
incidents = incidents_result.get('data', {}).get('incidents', []) \
            if incidents_result.get('status') == 'success' else []

# ============================================================
# ROW 1 — KPI METRICS  (4 cards)
# ============================================================
st.markdown('<p class="section-header">📈 Overview</p>', unsafe_allow_html=True)

total_incidents   = stats.get('total', len(incidents))
critical_count    = stats.get('critical', 0)
parent_notified   = stats.get('parent_notified', 0)

# "This week" — calculate from incidents list
today       = date.today()
week_start  = today - timedelta(days=7)
this_week   = sum(
    1 for i in incidents
    if i.get('incident_date') and i['incident_date'] >= week_start.isoformat()
)

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.markdown(f"""
    <div class="kpi-card" style="border-top: 4px solid #1f77b4;">
        <p class="kpi-label">📋 Total Incidents</p>
        <p class="kpi-value" style="color:#1f77b4;">{total_incidents}</p>
        <p class="kpi-sub">In selected period</p>
    </div>
    """, unsafe_allow_html=True)

with kpi2:
    st.markdown(f"""
    <div class="kpi-card" style="border-top: 4px solid #FFA500;">
        <p class="kpi-label">📅 This Week</p>
        <p class="kpi-value" style="color:#FFA500;">{this_week}</p>
        <p class="kpi-sub">Last 7 days</p>
    </div>
    """, unsafe_allow_html=True)

with kpi3:
    st.markdown(f"""
    <div class="kpi-card" style="border-top: 4px solid #FF4B4B;">
        <p class="kpi-label">🚨 Critical Cases</p>
        <p class="kpi-value" style="color:#FF4B4B;">{critical_count}</p>
        <p class="kpi-sub">Needs immediate attention</p>
    </div>
    """, unsafe_allow_html=True)

with kpi4:
    st.markdown(f"""
    <div class="kpi-card" style="border-top: 4px solid #00CC44;">
        <p class="kpi-label">📞 Parent Notified</p>
        <p class="kpi-value" style="color:#00CC44;">{parent_notified}</p>
        <p class="kpi-sub">Parents informed</p>
    </div>
    """, unsafe_allow_html=True)


st.markdown("---")

# ============================================================
# ROW 2 — LINE CHART (Trend) + PIE CHART (By Type)
# ============================================================
st.markdown('<p class="section-header">📊 Incident Trends & Distribution</p>', unsafe_allow_html=True)

row2_col1, row2_col2 = st.columns([3, 2])

# ── Line Chart: Daily Incident Trend ─────────────────────────
with row2_col1:
    trend_data = trends.get('trends', [])

    if trend_data:
        trend_df = pd.DataFrame(trend_data)
        trend_df['date']  = pd.to_datetime(trend_df['date'])
        trend_df['count'] = trend_df['count'].astype(int)

        # Fill missing dates with 0
        full_date_range = pd.date_range(
            start=date.today() - timedelta(days=days),
            end=date.today(),
            freq='D'
        )
        trend_df = (
            trend_df.set_index('date')
            .reindex(full_date_range, fill_value=0)
            .reset_index()
            .rename(columns={'index': 'date'})
        )

        fig_line = go.Figure()

        # Area fill under line
        fig_line.add_trace(go.Scatter(
            x=trend_df['date'],
            y=trend_df['count'],
            mode='lines+markers',
            name='Incidents',
            line=dict(color='#1f77b4', width=2.5),
            marker=dict(size=5, color='#1f77b4'),
            fill='tozeroy',
            fillcolor='rgba(31, 119, 180, 0.12)'
        ))

        fig_line.update_layout(
            title=dict(
                text=f"📈 Daily Incident Trend — Last {days} Days",
                font=dict(size=15, color='#1a202c')
            ),
            height=320,
            xaxis=dict(
                title='Date',
                showgrid=True,
                gridcolor='#f0f0f0',
                tickformat='%d %b'
            ),
            yaxis=dict(
                title='No. of Incidents',
                showgrid=True,
                gridcolor='#f0f0f0',
                rangemode='tozero'
            ),
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(color='#1a202c'),
            hovermode='x unified',
            margin=dict(t=50, b=40, l=50, r=20)
        )
        st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.markdown("""
        <div style='background:#f7fafc; border:1px dashed #cbd5e0;
                    border-radius:12px; padding:3rem; text-align:center;'>
            <p style='color:#a0aec0; font-size:1.1rem;'>
                📭 No trend data available for this period
            </p>
        </div>
        """, unsafe_allow_html=True)


# ── Pie Chart: Incidents by Type ─────────────────────────────
with row2_col2:
    type_data = stats.get('by_type', [])

    if type_data:
        type_df = pd.DataFrame(type_data)

        # Color palette for incident types
        type_colors = [
            '#1f77b4', '#FFA500', '#FF4B4B',
            '#00CC44', '#9467bd', '#8c564b', '#e377c2'
        ]

        fig_pie = go.Figure(data=[go.Pie(
            labels=type_df['type'],
            values=type_df['count'],
            marker=dict(colors=type_colors[:len(type_df)]),
            hole=0.42,
            textinfo='label+percent',
            textfont=dict(size=11),
            hovertemplate='<b>%{label}</b><br>Count: %{value}<br>%{percent}<extra></extra>'
        )])

        fig_pie.update_layout(
            title=dict(
                text="🥧 Incidents by Type",
                font=dict(size=15, color='#1a202c')
            ),
            height=320,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(color='#1a202c'),
            legend=dict(
                orientation='v',
                x=1.02,
                y=0.5,
                font=dict(size=10)
            ),
            margin=dict(t=50, b=20, l=10, r=10)
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.markdown("""
        <div style='background:#f7fafc; border:1px dashed #cbd5e0;
                    border-radius:12px; padding:3rem; text-align:center;'>
            <p style='color:#a0aec0; font-size:1.1rem;'>
                📭 No type data available for this period
            </p>
        </div>
        """, unsafe_allow_html=True)


st.markdown("---")

# ============================================================
# ROW 3 — SEVERITY BAR CHART + GRADE COMPARISON
# ============================================================
st.markdown('<p class="section-header">⚠️ Severity & Grade Analysis</p>', unsafe_allow_html=True)

row3_col1, row3_col2 = st.columns(2)

# ── Bar Chart: Incidents by Severity ─────────────────────────
with row3_col1:
    severity_data = stats.get('by_severity', [])

    if severity_data:
        sev_df = pd.DataFrame(severity_data)

        # Ensure correct order
        sev_order  = ['Minor', 'Moderate', 'Serious', 'Critical']
        sev_df['severity'] = pd.Categorical(
            sev_df['severity'],
            categories=sev_order,
            ordered=True
        )
        sev_df = sev_df.sort_values('severity')

        bar_colors = [
            SEVERITY_COLORS.get(s, '#ccc') for s in sev_df['severity']
        ]

        fig_bar = go.Figure(data=[go.Bar(
            x=sev_df['severity'],
            y=sev_df['count'],
            marker_color=bar_colors,
            text=sev_df['count'],
            textposition='outside',
            width=0.5,
            hovertemplate='<b>%{x}</b><br>Count: %{y}<extra></extra>'
        )])

        fig_bar.update_layout(
            title=dict(
                text="⚠️ Incidents by Severity",
                font=dict(size=15, color='#1a202c')
            ),
            height=320,
            xaxis=dict(title='Severity Level', showgrid=False),
            yaxis=dict(
                title='No. of Incidents',
                showgrid=True,
                gridcolor='#f0f0f0',
                rangemode='tozero'
            ),
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(color='#1a202c'),
            margin=dict(t=50, b=40, l=50, r=20)
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.markdown("""
        <div style='background:#f7fafc; border:1px dashed #cbd5e0;
                    border-radius:12px; padding:3rem; text-align:center;'>
            <p style='color:#a0aec0; font-size:1.1rem;'>
                📭 No severity data available
            </p>
        </div>
        """, unsafe_allow_html=True)


# ── Bar Chart: Incidents by Grade ────────────────────────────
with row3_col2:
    grade_data = stats.get('by_grade', [])

    if grade_data:
        grade_df = pd.DataFrame(grade_data)
        grade_df = grade_df.sort_values('grade')
        grade_df['grade_label'] = grade_df['grade'].apply(lambda g: f"Grade {g}")

        # Gradient blue shades per grade
        grade_colors = ['#c6dcf5', '#8db8e8', '#5592d6', '#2563eb', '#1a3f8f']

        fig_grade = go.Figure(data=[go.Bar(
            x=grade_df['grade_label'],
            y=grade_df['count'],
            marker_color=grade_colors[:len(grade_df)],
            text=grade_df['count'],
            textposition='outside',
            width=0.5,
            hovertemplate='<b>%{x}</b><br>Incidents: %{y}<extra></extra>'
        )])

        fig_grade.update_layout(
            title=dict(
                text="🎓 Incidents by Grade",
                font=dict(size=15, color='#1a202c')
            ),
            height=320,
            xaxis=dict(title='Grade', showgrid=False),
            yaxis=dict(
                title='No. of Incidents',
                showgrid=True,
                gridcolor='#f0f0f0',
                rangemode='tozero'
            ),
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(color='#1a202c'),
            margin=dict(t=50, b=40, l=50, r=20)
        )
        st.plotly_chart(fig_grade, use_container_width=True)
    else:
        st.markdown("""
        <div style='background:#f7fafc; border:1px dashed #cbd5e0;
                    border-radius:12px; padding:3rem; text-align:center;'>
            <p style='color:#a0aec0; font-size:1.1rem;'>
                📭 No grade data available
            </p>
        </div>
        """, unsafe_allow_html=True)



st.markdown("---")

# ============================================================
# ROW 4 — TOP 10 MOST FREQUENT INCIDENT STUDENTS
# ============================================================
st.markdown('<p class="section-header">🏮 Top 10 Students by Incidents</p>', unsafe_allow_html=True)

if incidents:
    # ── Build student incident summary from fetched incidents ──
    student_summary = {}

    for inc in incidents:
        sid = inc.get('student_id')
        if sid not in student_summary:
            student_summary[sid] = {
                'student_id':      sid,
                'total':           0,
                'critical':        0,
                'serious':         0,
                'parent_notified': 0,
                'latest_date':     '',
                'types':           []
            }

        student_summary[sid]['total']  += 1
        student_summary[sid]['types'].append(inc.get('incident_type', ''))
        student_summary[sid]['latest_date'] = max(
            student_summary[sid]['latest_date'],
            inc.get('incident_date', '')
        )

        if inc.get('severity') == 'Critical':
            student_summary[sid]['critical'] += 1
        if inc.get('severity') == 'Serious':
            student_summary[sid]['serious']  += 1
        if inc.get('parent_notified'):
            student_summary[sid]['parent_notified'] += 1

    # Sort by total incidents desc → top 10
    top10 = sorted(
        student_summary.values(),
        key=lambda x: x['total'],
        reverse=True
    )[:10]

    if top10:
        # Build display dataframe
        top10_rows = []
        for rank, s in enumerate(top10, 1):
            # Risk tag based on critical + serious count
            combined_risk = s['critical'] + s['serious']
            if s['critical'] > 0:
                risk_tag = "🚨 Critical"
            elif s['serious'] > 0:
                risk_tag = "🔴 Serious"
            elif combined_risk == 0 and s['total'] > 3:
                risk_tag = "🟠 Watch"
            else:
                risk_tag = "🟢 Monitor"

            # Most common incident type
            most_common_type = (
                max(set(s['types']), key=s['types'].count)
                if s['types'] else '—'
            )

            top10_rows.append({
                'Rank':            f"#{rank}",
                'Student ID':      s['student_id'],
                'Total Incidents': s['total'],
                'Critical':        s['critical'],
                'Serious':         s['serious'],
                'Parent Notified': s['parent_notified'],
                'Most Common':     most_common_type,
                'Latest Date':     s['latest_date'],
                'Status':          risk_tag
            })

        top10_df = pd.DataFrame(top10_rows)

        # ── Color-code Status column using styler ──────────────
        def highlight_status(val):
            if '🚨' in str(val):
                return 'background-color:#fff5f5; color:#c53030; font-weight:700;'
            elif '🔴' in str(val):
                return 'background-color:#fff8f0; color:#c05621; font-weight:700;'
            elif '🟠' in str(val):
                return 'background-color:#fffbeb; color:#b7791f; font-weight:600;'
            else:
                return 'background-color:#f0fff4; color:#276749; font-weight:600;'

        styled_df = top10_df.style.applymap(
            highlight_status, subset=['Status']
        )

        st.dataframe(
            styled_df,
            use_container_width=True,
            hide_index=True
        )

        # ── Quick action buttons below table ──────────────────
        st.markdown("---")
        qa1, qa2, qa3 = st.columns(3)

        with qa1:
            if st.button(
                "📝 Log New Incident",
                use_container_width=True,
                type="primary"
            ):
                st.switch_page("pages/6_📝_Incident_Logging.py")

        with qa2:
            # CSV Export
            csv_data = top10_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Export Top 10 as CSV",
                data=csv_data,
                file_name=f"top10_incidents_{date.today().isoformat()}.csv",
                mime="text/csv",
                use_container_width=True
            )

        with qa3:
            if st.button(
                "👥 View All Students",
                use_container_width=True
            ):
                st.switch_page("pages/2_👥_Students.py")

    else:
        st.info("ℹ️ No student incident data to rank.")

else:
    st.markdown("""
    <div style='background:#f7fafc; border:1px dashed #cbd5e0;
                border-radius:12px; padding:3rem; text-align:center;'>
        <p style='color:#a0aec0; font-size:1.2rem; margin:0;'>
            🎉 No incidents recorded in the selected period!
        </p>
        <p style='color:#718096; margin-top:0.5rem;'>
            Try changing the date range or filters above.
        </p>
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# FOOTER SUMMARY BAR
# ============================================================
st.markdown("---")
footer_c1, footer_c2, footer_c3, footer_c4 = st.columns(4)

with footer_c1:
    st.markdown(f"""
    <div style='text-align:center; color:#4a5568; font-size:0.85rem;'>
        🕐 <b>Last Refreshed</b><br/>
        {datetime.now().strftime('%d %b %Y, %I:%M %p')}
    </div>
    """, unsafe_allow_html=True)

with footer_c2:
    st.markdown(f"""
    <div style='text-align:center; color:#4a5568; font-size:0.85rem;'>
        📅 <b>Period</b><br/>
        {(date.today() - timedelta(days=days)).isoformat()} → {date.today().isoformat()}
    </div>
    """, unsafe_allow_html=True)

with footer_c3:
    st.markdown(f"""
    <div style='text-align:center; color:#4a5568; font-size:0.85rem;'>
        🎓 <b>Grade Filter</b><br/>
        {grade_filter}
    </div>
    """, unsafe_allow_html=True)

with footer_c4:
    st.markdown(f"""
    <div style='text-align:center; color:#4a5568; font-size:0.85rem;'>
        📌 <b>Type Filter</b><br/>
        {type_filter}
    </div>
    """, unsafe_allow_html=True)
