"""
Batch Risk Analysis
ScholarSense - AI-Powered Academic Intelligence System
Enhancement 8: Run bulk ML predictions & view school-wide risk overview
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
    page_title="Batch Analysis - ScholarSense",
    page_icon="🔁",
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
        background: white; padding: 1.4rem 1.2rem;
        border-radius: 14px; border: 1px solid #e2e8f0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        text-align: center; margin-bottom: 1rem;
    }
    .kpi-value {
        font-size: 2.2rem; font-weight: 800;
        margin: 0.2rem 0; line-height: 1.1;
    }
    .kpi-label {
        font-size: 0.8rem; color: #4a5568;
        font-weight: 600; text-transform: uppercase;
        letter-spacing: 0.04em;
    }
    .kpi-sub {
        font-size: 0.78rem; color: #718096; margin-top: 0.3rem;
    }
    .section-header {
        color: #1a202c; font-size: 1.3rem; font-weight: 700;
        margin: 1.5rem 0 1rem 0; padding-bottom: 0.4rem;
        border-bottom: 3px solid #2563eb; display: inline-block;
    }
    .run-box {
        background: white; padding: 1.5rem 2rem;
        border-radius: 14px; border: 2px dashed #2563eb;
        margin-bottom: 1.5rem;
    }
    .risk-critical { color: #8B0000; font-weight: 700; }
    .risk-high     { color: #FF4B4B; font-weight: 700; }
    .risk-medium   { color: #FFA500; font-weight: 700; }
    .risk-low      { color: #00CC44; font-weight: 700; }
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

RISK_LEVELS = ['All', 'Critical', 'High', 'Medium', 'Low']

RISK_COLORS = {
    'Low':      '#00CC44',
    'Medium':   '#FFA500',
    'High':     '#FF4B4B',
    'Critical': '#8B0000'
}

RISK_ICONS = {
    'Low':      '🟢',
    'Medium':   '🟠',
    'High':     '🔴',
    'Critical': '🚨'
}

GRADES   = [6, 7, 8, 9, 10]
SECTIONS = ['All', 'A', 'B', 'C', 'D']

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
            timeout=30
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
            timeout=120    # batch can take time
        )
        return r.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}

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
    if st.button("📊 Dashboard",             use_container_width=True):
        st.switch_page("pages/1_📊_Dashboard.py")
    if st.button("👥 Students",              use_container_width=True):
        st.switch_page("pages/2_👥_Students.py")
    if st.button("🎯 Predictions",           use_container_width=True):
        st.switch_page("pages/4_🎯_Predictions.py")
    if st.button("📝 Marks Entry",           use_container_width=True):
        st.switch_page("pages/9_📝_Marks_Entry.py")
    if st.button("🧠 Behavioral Dashboard",  use_container_width=True):
        st.switch_page("pages/8_🧠_Behavioral_Dashboard.py")
    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True, type="primary"):
        SessionManager.logout()
        st.switch_page("app.py")

# ============================================
# PAGE HEADER
# ============================================
st.markdown("""
    <h1 style='color:#1a202c; margin-bottom:0;'>🔁 Batch Risk Analysis</h1>
    <p style='color:#4a5568; margin-top:0.25rem;'>
        Run ML risk predictions for all students at once
        and view school-wide risk overview
    </p>
    <hr style='border:none; border-top:1px solid #e2e8f0; margin:1rem 0;'/>
""", unsafe_allow_html=True)

# ============================================
# TABS
# ============================================
tab1, tab2, tab3 = st.tabs([
    "🔁 Run Batch",
    "📋 All Predictions",
    "📊 Risk Overview"
])


# ============================================================
# TAB 1 — RUN BATCH
# ============================================================
with tab1:
    st.markdown("### 🔁 Run Batch Predictions")
    st.markdown(
        "Trigger the ML model for all students at once. "
        "Results are saved and available in the **All Predictions** tab."
    )
    st.markdown("---")

    # ── Batch Run Controls ─────────────────────────────────
    st.markdown('<div class="run-box">', unsafe_allow_html=True)
    st.markdown("#### ⚙️ Configure Batch Run")
    st.caption(
        "Leave filters as 'All' to run predictions for **every active student**."
    )

    rc1, rc2, rc3 = st.columns(3)
    with rc1:
        run_grade = st.selectbox(
            "🎓 Grade Filter",
            options=['All Grades'] + GRADES,
            key="run_grade"
        )
    with rc2:
        run_section = st.selectbox(
            "🏫 Section Filter",
            options=SECTIONS,
            key="run_section"
        )
    with rc3:
        st.markdown("<br/>", unsafe_allow_html=True)
        # Show unpredicted count
        with st.spinner(""):
            unpred = api_get("/batch/unpredicted")
        unpred_count = unpred.get('data', {}).get('total', '?') \
                       if unpred.get('status') == 'success' else '?'
        st.info(f"⚠️ **{unpred_count}** students have no prediction yet")

    st.markdown("</div>", unsafe_allow_html=True)

    # ── Run Button ─────────────────────────────────────────
    col_btn1, col_btn2, col_btn3 = st.columns([2, 1, 1])
    with col_btn1:
        run_btn = st.button(
            "🚀 Run Batch Predictions Now",
            use_container_width=True,
            type="primary"
        )
    with col_btn2:
        st.markdown(
            "<p style='color:#4a5568; font-size:0.85rem; "
            "padding-top:0.6rem;'>⏱️ May take 1-2 minutes</p>",
            unsafe_allow_html=True
        )

    # ── Handle Batch Run ───────────────────────────────────
    if run_btn:
        payload = {}
        if run_grade != 'All Grades':
            payload['grade']   = run_grade
        if run_section != 'All':
            payload['section'] = run_section

        progress_bar = st.progress(0, text="🔁 Starting batch prediction...")

        with st.spinner(
            f"🤖 Running ML predictions... "
            f"{'(All students)' if not payload else str(payload)}"
        ):
            progress_bar.progress(30, text="🔄 Fetching students...")
            result = api_post("/batch/run", payload)
            progress_bar.progress(90, text="💾 Saving predictions...")

        progress_bar.progress(100, text="✅ Done!")

        if result.get('status') == 'success':
            summary = result['data']['summary']
            results = result['data']['results']

            st.success(
                f"✅ Batch complete! "
                f"**{summary['success']}** predicted | "
                f"**{summary['skipped']}** skipped | "
                f"**{summary['failed']}** failed"
            )
            st.balloons()

            # ── Summary Cards ──────────────────────────────
            st.markdown("---")
            st.markdown("#### 📊 Batch Run Summary")

            s1, s2, s3, s4, s5 = st.columns(5)
            with s1:
                st.markdown(f"""
                <div class="kpi-card" style="border-top:4px solid #1f77b4;">
                    <p class="kpi-label">👥 Total Students</p>
                    <p class="kpi-value" style="color:#1f77b4;">
                        {summary['total']}
                    </p>
                </div>
                """, unsafe_allow_html=True)
            with s2:
                st.markdown(f"""
                <div class="kpi-card" style="border-top:4px solid #00CC44;">
                    <p class="kpi-label">✅ Predicted</p>
                    <p class="kpi-value" style="color:#00CC44;">
                        {summary['success']}
                    </p>
                </div>
                """, unsafe_allow_html=True)
            with s3:
                st.markdown(f"""
                <div class="kpi-card" style="border-top:4px solid #FFA500;">
                    <p class="kpi-label">⏭️ Skipped</p>
                    <p class="kpi-value" style="color:#FFA500;">
                        {summary['skipped']}
                    </p>
                    <p class="kpi-sub">No academic data</p>
                </div>
                """, unsafe_allow_html=True)
            with s4:
                st.markdown(f"""
                <div class="kpi-card" style="border-top:4px solid #FF4B4B;">
                    <p class="kpi-label">❌ Failed</p>
                    <p class="kpi-value" style="color:#FF4B4B;">
                        {summary['failed']}
                    </p>
                    <p class="kpi-sub">ML error</p>
                </div>
                """, unsafe_allow_html=True)
            with s5:
                critical = summary['risk_summary'].get('Critical', 0)
                st.markdown(f"""
                <div class="kpi-card" style="border-top:4px solid #8B0000;">
                    <p class="kpi-label">🚨 Critical Risk</p>
                    <p class="kpi-value" style="color:#8B0000;">
                        {critical}
                    </p>
                    <p class="kpi-sub">Needs attention</p>
                </div>
                """, unsafe_allow_html=True)

            # ── Risk Distribution from this run ────────────
            st.markdown("---")
            risk_sum = summary['risk_summary']
            rc1, rc2 = st.columns([1, 2])

            with rc1:
                st.markdown("#### 🎯 Risk Distribution")
                for level in ['Critical', 'High', 'Medium', 'Low']:
                    count = risk_sum.get(level, 0)
                    icon  = RISK_ICONS.get(level, '')
                    color = RISK_COLORS.get(level, '#ccc')
                    st.markdown(
                        f"<p style='font-size:1.1rem; margin:0.3rem 0;'>"
                        f"{icon} <b style='color:{color};'>{level}</b>: "
                        f"<b>{count}</b> students</p>",
                        unsafe_allow_html=True
                    )

            with rc2:
                # Donut chart of this run's risk distribution
                labels = [k for k, v in risk_sum.items() if v > 0]
                values = [v for v in risk_sum.values() if v > 0]
                colors = [RISK_COLORS.get(l, '#ccc') for l in labels]

                if values:
                    fig_run = go.Figure(data=[go.Pie(
                        labels=labels,
                        values=values,
                        marker=dict(colors=colors),
                        hole=0.45,
                        textinfo='label+value+percent',
                        textfont=dict(size=12),
                        hovertemplate=(
                            '<b>%{label}</b><br>'
                            'Students: %{value}<br>'
                            '%{percent}<extra></extra>'
                        )
                    )])
                    fig_run.update_layout(
                        title="Risk Distribution — This Run",
                        height=300,
                        plot_bgcolor='white',
                        paper_bgcolor='white',
                        font=dict(color='#1a202c'),
                        margin=dict(t=40, b=10, l=10, r=10),
                        showlegend=False
                    )
                    st.plotly_chart(fig_run, use_container_width=True)

            # ── Per-student results table ──────────────────
            st.markdown("---")
            st.markdown("#### 📋 Per-Student Results")

            success_results = [r for r in results if r['status'] == 'success']
            skipped_results = [r for r in results if r['status'] == 'skipped']
            failed_results  = [r for r in results if r['status'] == 'failed']

            res_tab1, res_tab2, res_tab3 = st.tabs([
                f"✅ Predicted ({len(success_results)})",
                f"⏭️ Skipped ({len(skipped_results)})",
                f"❌ Failed ({len(failed_results)})"
            ])

            with res_tab1:
                if success_results:
                    suc_rows = []
                    for r in success_results:
                        icon = RISK_ICONS.get(r.get('risk_label', ''), '')
                        suc_rows.append({
                            'Student':    r['student_name'],
                            'ID':         r['student_code'],
                            'Grade':      f"{r['grade']}{r.get('section','')}",
                            'Risk':       f"{icon} {r['risk_label']}",
                            'Confidence': f"{r['confidence_score']:.1f}%",
                            'GPA':        f"{r['gpa']:.1f}%",
                            'Failed Subs':r['failed_subjects']
                        })
                    suc_df = pd.DataFrame(suc_rows)

                    def highlight_risk(val):
                        if '🚨' in str(val):
                            return 'background:#fff0f0; color:#8B0000; font-weight:700;'
                        elif '🔴' in str(val):
                            return 'background:#fff5f0; color:#c53030; font-weight:700;'
                        elif '🟠' in str(val):
                            return 'background:#fffbeb; color:#b7791f; font-weight:600;'
                        else:
                            return 'background:#f0fff4; color:#276749; font-weight:600;'

                    styled_suc = suc_df.style.applymap(
                        highlight_risk, subset=['Risk']
                    )
                    st.dataframe(
                        styled_suc,
                        use_container_width=True,
                        hide_index=True
                    )

                    # Export
                    csv = suc_df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        "📥 Export Results as CSV",
                        data=csv,
                        file_name=f"batch_results_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )

            with res_tab2:
                if skipped_results:
                    skip_df = pd.DataFrame([{
                        'Student': r['student_name'],
                        'ID':      r['student_code'],
                        'Grade':   f"{r['grade']}{r.get('section','')}",
                        'Reason':  r.get('reason', '—')
                    } for r in skipped_results])
                    st.dataframe(skip_df, use_container_width=True, hide_index=True)
                    st.warning(
                        "⚠️ These students need academic records "
                        "entered before predictions can run."
                    )
                else:
                    st.success("✅ No students were skipped!")

            with res_tab3:
                if failed_results:
                    fail_df = pd.DataFrame([{
                        'Student': r['student_name'],
                        'ID':      r['student_code'],
                        'Grade':   f"{r['grade']}{r.get('section','')}",
                        'Error':   r.get('reason', '—')
                    } for r in failed_results])
                    st.dataframe(fail_df, use_container_width=True, hide_index=True)
                else:
                    st.success("✅ No prediction failures!")

        else:
            st.error(f"❌ Batch failed: {result.get('message', 'Unknown error')}")


# ============================================================
# TAB 2 — ALL PREDICTIONS
# ============================================================
with tab2:
    st.markdown("### 📋 All Student Predictions")
    st.markdown("View latest stored predictions. Use filters to drill down.")
    st.markdown("---")

    # ── Filters ───────────────────────────────────────────
    pf1, pf2, pf3, pf4, pf5 = st.columns(5)

    with pf1:
        p_grade = st.selectbox(
            "🎓 Grade",
            options=['All'] + GRADES,
            key="p_grade"
        )
    with pf2:
        p_section = st.selectbox(
            "🏫 Section",
            options=SECTIONS,
            key="p_section"
        )
    with pf3:
        p_risk = st.selectbox(
            "⚠️ Risk Level",
            options=RISK_LEVELS,
            key="p_risk"
        )
    with pf4:
        p_limit = st.selectbox(
            "📊 Show",
            options=[50, 100, 200, 500],
            index=1,
            key="p_limit"
        )
    with pf5:
        st.markdown("<br/>", unsafe_allow_html=True)
        p_refresh = st.button(
            "🔄 Refresh",
            use_container_width=True,
            key="p_refresh"
        )

    st.markdown("---")

    # ── Fetch predictions ──────────────────────────────────
    p_params = {"limit": p_limit}
    if p_grade != 'All':
        p_params['grade']      = p_grade
    if p_section != 'All':
        p_params['section']    = p_section
    if p_risk != 'All':
        p_params['risk_label'] = p_risk

    with st.spinner("Loading predictions..."):
        pred_result = api_get("/batch/predictions", params=p_params)

    if pred_result.get('status') != 'success':
        st.error(f"❌ {pred_result.get('message', 'Could not load predictions')}")
    else:
        pred_data    = pred_result.get('data', {})
        students     = pred_data.get('students', [])
        total        = pred_data.get('total', 0)
        risk_summary = pred_data.get('risk_summary', {})

        # ── Risk level metrics ─────────────────────────────
        mc1, mc2, mc3, mc4, mc5 = st.columns(5)
        mc1.metric("👥 Showing",            total)
        mc2.metric("🚨 Critical",           risk_summary.get('Critical', 0))
        mc3.metric("🔴 High",               risk_summary.get('High', 0))
        mc4.metric("🟠 Medium",             risk_summary.get('Medium', 0))
        mc5.metric("🟢 Low",                risk_summary.get('Low', 0))

        st.markdown("---")

        if not students:
            st.info(
                "ℹ️ No predictions found. "
                "Run batch predictions in the **Run Batch** tab first."
            )
        else:
            # ── Predictions table ──────────────────────────
            table_rows = []
            for s in students:
                icon = RISK_ICONS.get(s.get('risk_label', ''), '')
                predicted_at = s.get('predicted_at', '')
                if predicted_at:
                    try:
                        predicted_at = datetime.fromisoformat(
                            predicted_at
                        ).strftime('%d %b %Y %I:%M %p')
                    except Exception:
                        pass

                table_rows.append({
                    'Student':      s['student_name'],
                    'ID':           s['student_code'],
                    'Grade':        f"{s['grade']}{s.get('section','')}",
                    'Risk Level':   f"{icon} {s['risk_label']}",
                    'Confidence':   f"{s['confidence_score']:.1f}%",
                    'P(Critical)':  f"{s['probability_critical']:.1f}%",
                    'P(High)':      f"{s['probability_high']:.1f}%",
                    'P(Medium)':    f"{s['probability_medium']:.1f}%",
                    'P(Low)':       f"{s['probability_low']:.1f}%",
                    'Predicted At': predicted_at
                })

            table_df = pd.DataFrame(table_rows)

            def style_risk_col(val):
                if '🚨' in str(val):
                    return 'background:#fff0f0; color:#8B0000; font-weight:700;'
                elif '🔴' in str(val):
                    return 'background:#fff5f0; color:#c53030; font-weight:700;'
                elif '🟠' in str(val):
                    return 'background:#fffbeb; color:#b7791f; font-weight:600;'
                else:
                    return 'background:#f0fff4; color:#276749; font-weight:600;'

            styled_table = table_df.style.applymap(
                style_risk_col, subset=['Risk Level']
            )

            st.dataframe(
                styled_table,
                use_container_width=True,
                hide_index=True
            )

            # ── Export ─────────────────────────────────────
            csv_all = table_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Export All Predictions as CSV",
                data=csv_all,
                file_name=(
                    f"predictions_"
                    f"{'grade'+str(p_grade) if p_grade != 'All' else 'all'}_"
                    f"{datetime.now().strftime('%Y%m%d')}.csv"
                ),
                mime="text/csv",
                use_container_width=True
            )


# ============================================================
# TAB 3 — RISK OVERVIEW
# ============================================================
with tab3:
    st.markdown("### 📊 School-Wide Risk Overview")
    st.markdown("---")

    with st.spinner("Loading school-wide risk summary..."):
        summary_result = api_get("/batch/summary")
        unpred_result  = api_get("/batch/unpredicted")

    if summary_result.get('status') != 'success':
        st.error(f"❌ {summary_result.get('message', 'Could not load summary')}")
    else:
        sum_data     = summary_result.get('data', {})
        risk_sum     = sum_data.get('risk_summary', {})
        total_active = sum_data.get('total_active', 0)
        total_pred   = sum_data.get('total_predicted', 0)
        total_unpred = sum_data.get('total_unpredicted', 0)
        avg_conf     = sum_data.get('avg_confidence', 0)

        # ── Top KPI Row ────────────────────────────────────
        st.markdown(
            '<p class="section-header">🏫 School Overview</p>',
            unsafe_allow_html=True
        )

        ov1, ov2, ov3, ov4, ov5, ov6 = st.columns(6)

        with ov1:
            st.markdown(f"""
            <div class="kpi-card" style="border-top:4px solid #1f77b4;">
                <p class="kpi-label">👥 Active Students</p>
                <p class="kpi-value" style="color:#1f77b4;">{total_active}</p>
            </div>
            """, unsafe_allow_html=True)
        with ov2:
            st.markdown(f"""
            <div class="kpi-card" style="border-top:4px solid #00CC44;">
                <p class="kpi-label">✅ Predicted</p>
                <p class="kpi-value" style="color:#00CC44;">{total_pred}</p>
            </div>
            """, unsafe_allow_html=True)
        with ov3:
            st.markdown(f"""
            <div class="kpi-card" style="border-top:4px solid #FFA500;">
                <p class="kpi-label">⏳ Not Yet</p>
                <p class="kpi-value" style="color:#FFA500;">{total_unpred}</p>
                <p class="kpi-sub">No prediction yet</p>
            </div>
            """, unsafe_allow_html=True)
        with ov4:
            st.markdown(f"""
            <div class="kpi-card" style="border-top:4px solid #8B0000;">
                <p class="kpi-label">🚨 Critical</p>
                <p class="kpi-value" style="color:#8B0000;">
                    {risk_sum.get('Critical', 0)}
                </p>
            </div>
            """, unsafe_allow_html=True)
        with ov5:
            st.markdown(f"""
            <div class="kpi-card" style="border-top:4px solid #FF4B4B;">
                <p class="kpi-label">🔴 High Risk</p>
                <p class="kpi-value" style="color:#FF4B4B;">
                    {risk_sum.get('High', 0)}
                </p>
            </div>
            """, unsafe_allow_html=True)
        with ov6:
            st.markdown(f"""
            <div class="kpi-card" style="border-top:4px solid #2563eb;">
                <p class="kpi-label">🎯 Avg Confidence</p>
                <p class="kpi-value" style="color:#2563eb;">{avg_conf}%</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # ── Charts Row ─────────────────────────────────────
        st.markdown(
            '<p class="section-header">📊 Risk Distribution</p>',
            unsafe_allow_html=True
        )

        ch1, ch2 = st.columns(2)

        # Donut chart
        with ch1:
            labels = [k for k, v in risk_sum.items() if v > 0]
            values = [v for k, v in risk_sum.items() if v > 0]
            colors = [RISK_COLORS.get(l, '#ccc') for l in labels]

            if values:
                fig_donut = go.Figure(data=[go.Pie(
                    labels=labels,
                    values=values,
                    marker=dict(colors=colors),
                    hole=0.5,
                    textinfo='label+value+percent',
                    textfont=dict(size=12),
                    hovertemplate=(
                        '<b>%{label}</b><br>'
                        'Students: %{value}<br>'
                        '%{percent}<extra></extra>'
                    )
                )])
                fig_donut.update_layout(
                    title="🎯 School-wide Risk Distribution",
                    height=350,
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    font=dict(color='#1a202c'),
                    margin=dict(t=50, b=20, l=10, r=10),
                    showlegend=True,
                    legend=dict(orientation='v', x=1.02, y=0.5)
                )
                st.plotly_chart(fig_donut, use_container_width=True)
            else:
                st.info("ℹ️ No prediction data yet.")

        # Horizontal bar chart
        with ch2:
            risk_order  = ['Critical', 'High', 'Medium', 'Low']
            bar_labels  = [r for r in risk_order if risk_sum.get(r, 0) > 0]
            bar_values  = [risk_sum.get(r, 0) for r in bar_labels]
            bar_colors  = [RISK_COLORS.get(r, '#ccc') for r in bar_labels]

            if bar_values:
                fig_bar = go.Figure(data=[go.Bar(
                    y=bar_labels,
                    x=bar_values,
                    orientation='h',
                    marker_color=bar_colors,
                    text=bar_values,
                    textposition='outside',
                    hovertemplate='<b>%{y}</b><br>Students: %{x}<extra></extra>'
                )])
                fig_bar.update_layout(
                    title="📊 Students per Risk Level",
                    height=350,
                    xaxis=dict(
                        title='Number of Students',
                        showgrid=True,
                        gridcolor='#f0f0f0'
                    ),
                    yaxis=dict(title='Risk Level', showgrid=False),
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    font=dict(color='#1a202c'),
                    margin=dict(t=50, b=40, l=80, r=40)
                )
                st.plotly_chart(fig_bar, use_container_width=True)

        st.markdown("---")

        # ── Unpredicted Students Table ─────────────────────
        st.markdown(
            '<p class="section-header">⏳ Students Without Predictions</p>',
            unsafe_allow_html=True
        )

        if unpred_result.get('status') == 'success':
            unpred_list = unpred_result['data'].get('students', [])

            if unpred_list:
                st.warning(
                    f"⚠️ **{len(unpred_list)}** student(s) have never been "
                    f"analysed. Go to **Run Batch** tab to predict them."
                )
                unpred_df = pd.DataFrame([{
                    'Student':  s['student_name'],
                    'ID':       s['student_code'],
                    'Grade':    f"{s['grade']}{s.get('section', '')}"
                } for s in unpred_list])
                st.dataframe(
                    unpred_df,
                    use_container_width=True,
                    hide_index=True
                )

                # Quick run button
                if st.button(
                    "🚀 Run Predictions for These Students Now",
                    type="primary",
                    use_container_width=True
                ):
                    with st.spinner("🤖 Running predictions..."):
                        quick_result = api_post("/batch/run", {})
                    if quick_result.get('status') == 'success':
                        st.success("✅ Done! Refresh to see updated results.")
                        st.rerun()
                    else:
                        st.error(
                            f"❌ {quick_result.get('message', 'Failed')}"
                        )
            else:
                st.success(
                    "🎉 All active students have at least one prediction!"
                )

        # ── Footer ─────────────────────────────────────────
        st.markdown("---")
        st.markdown(f"""
        <p style='color:#718096; font-size:0.82rem; text-align:center;'>
            🕐 Page loaded at {datetime.now().strftime('%d %b %Y, %I:%M %p')}
            &nbsp;|&nbsp; Data reflects latest stored predictions
        </p>
        """, unsafe_allow_html=True)
