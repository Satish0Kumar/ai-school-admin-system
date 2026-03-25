"""
ScholarSense - Shared Sidebar Navigation
Import and call render_sidebar() at the top of every page
"""
import streamlit as st
from frontend.utils.session_manager import SessionManager

def render_sidebar():
    """Render grouped navigation sidebar with user info"""

    with st.sidebar:

        st.markdown("""
        <style>
            /* Hide Streamlit's auto-generated pages nav — always */
            [data-testid="stSidebarNav"] {
                display: none !important;
            }
            /* Mobile padding fix */
            @media (max-width: 768px) {
                [data-testid="stSidebar"] > div:first-child {
                    padding-top: 1rem !important;
                }
            }
        </style>

        <div style='text-align:center; padding: 10px 0 5px 0;'>
            <span style='font-size:2rem;'>🎓</span><br>
            <span style='font-weight:800; font-size:1.2rem; color:#1a202c;'>ScholarSense</span><br>
            <span style='font-size:0.75rem; color:#6b7280;'>AI Academic Intelligence</span>
        </div>
        """, unsafe_allow_html=True)


        # ── Dark Mode Toggle ───────────────────────────────
        dark_mode = st.toggle(
            "🌙 Dark Mode",
            value=st.session_state.get('dark_mode', False),   # ← False = light mode by default
            key="dark_mode_toggle"
        )
        st.session_state['dark_mode'] = dark_mode

        st.divider()


        # ── Get user role ──────────────────────────────────────
        user = st.session_state.get("user") or {}
        role = user.get("role", "teacher")

        # ══════════════════════════════════════════════════════
        # 📊 OVERVIEW
        # ══════════════════════════════════════════════════════
        st.markdown("**📊 OVERVIEW**")
        st.page_link("pages/1_📊_Dashboard.py",       label="  Dashboard",        icon="🏠")

        st.markdown("")

        # ══════════════════════════════════════════════════════
        # 👨‍🎓 STUDENTS
        # ══════════════════════════════════════════════════════
        st.markdown("**👨‍🎓 STUDENTS**")
        st.page_link("pages/2_👥_Students.py",         label="  All Students",     icon="👥")
        st.page_link("pages/3_👤_Student_Profile.py",  label="  Student Profile",  icon="👤")
        st.page_link("pages/9_📝_Marks_Entry.py",      label="  Marks Entry",      icon="📝")

        st.markdown("")

        # ══════════════════════════════════════════════════════
        # 🤖 RISK & AI
        # ══════════════════════════════════════════════════════
        st.markdown("**🤖 RISK & AI**")
        st.page_link("pages/4_🎯_Predictions.py",      label="  Risk Predictions", icon="🎯")
        st.page_link("pages/10_🔁_Batch_Analysis.py",  label="  Batch Analysis",   icon="🔁")
        st.page_link("pages/12_📈_Analytics.py",       label="  Analytics",        icon="📈")

        st.markdown("")

        # ══════════════════════════════════════════════════════
        # 📋 BEHAVIOUR
        # ══════════════════════════════════════════════════════
        st.markdown("**📋 BEHAVIOUR**")
        st.page_link("pages/5_📅_Attendance.py",           label="  Attendance",           icon="📅")
        st.page_link("pages/6_📝_Incident_Logging.py",     label="  Incident Logging",     icon="🚨")
        st.page_link("pages/8_🧠_Behavioral_Dashboard.py", label="  Behavioral Dashboard", icon="🧠")

        st.markdown("")

        # ══════════════════════════════════════════════════════
        # 📬 COMMUNICATION
        # ══════════════════════════════════════════════════════
        st.markdown("**📬 COMMUNICATION**")
        st.page_link("pages/7_🔔_Notifications.py",    label="  Notifications",    icon="🔔")
        st.page_link("pages/11_📧_Parent_Portal.py",   label="  Parent Portal",    icon="📧")

        # ══════════════════════════════════════════════════════
        # ⚙️ ADMIN ONLY — Hidden from teachers
        # ══════════════════════════════════════════════════════
        if role == "admin":
            st.markdown("")
            st.markdown("**⚙️ ADMIN**")
            st.page_link("pages/14_👤_User_Management.py", label="  User Management", icon="👤")

        # ── Bottom: User Info + Logout ─────────────────────────
        st.divider()

        name     = user.get("full_name", "User")
        role_badge = "🔑 Admin" if role == "admin" else "🏫 Teacher"

        st.markdown(f"""
        <div style='padding: 8px; background:#f8fafc;
                    border-radius:8px; border:1px solid #e2e8f0;'>
            <div style='font-weight:700; color:#1a202c; font-size:0.9rem;'>
                👤 {name}
            </div>
            <div style='color:#6b7280; font-size:0.8rem; margin-top:2px;'>
                {role_badge}
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🚪 Logout", use_container_width=True, type="secondary"):
                SessionManager.logout()
                st.switch_page("app.py")
        with col2:
            if st.button("🧹 Clear Cache", use_container_width=True, type="secondary", help="Clear saved session to require fresh login"):
                SessionManager.clear_session_cache()
                st.success("✓ Session cache cleared! Please reload the page.")
                st.balloons()

        # ── Preferences Panel ──────────────────────────────────
        from frontend.utils.preferences import render_preferences_panel
        render_preferences_panel()

        # ── Keyboard shortcut hints ────────────────────────────
        from frontend.utils.ui_helpers import show_shortcut_hints, inject_keyboard_shortcuts
        show_shortcut_hints()
        inject_keyboard_shortcuts()

       