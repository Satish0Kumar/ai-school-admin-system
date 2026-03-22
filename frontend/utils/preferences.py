"""
User Preferences — Stores and applies user preferences across the app.
All preferences saved in session_state (persist during session).
"""
import streamlit as st


# ── Defaults ─────────────────────────────────────────────────
DEFAULTS = {
    "font_size":      "Medium",   # Small | Medium | Large
    "items_per_page": 10,         # 5 | 10 | 25 | 50
    "date_format":    "DD MMM YYYY",  # options below
    "default_page":   "Dashboard",
    "show_tooltips":  True,
    "compact_mode":   False,
}

DATE_FORMATS = ["DD MMM YYYY", "DD/MM/YYYY", "MM/DD/YYYY", "YYYY-MM-DD"]
FONT_SIZES   = ["Small", "Medium", "Large"]
PAGE_SIZES   = [5, 10, 25, 50]
DEFAULT_PAGES = ["Dashboard", "Students", "Predictions", "Analytics"]


def get_pref(key: str):
    """Get a preference value, falling back to default."""
    prefs = st.session_state.get("user_prefs", {})
    return prefs.get(key, DEFAULTS[key])


def set_pref(key: str, value):
    """Set a single preference value."""
    if "user_prefs" not in st.session_state:
        st.session_state["user_prefs"] = dict(DEFAULTS)
    st.session_state["user_prefs"][key] = value


def init_prefs():
    """Initialize preferences with defaults if not set."""
    if "user_prefs" not in st.session_state:
        st.session_state["user_prefs"] = dict(DEFAULTS)


def apply_font_size():
    """Inject CSS for chosen font size."""
    size_map = {
        "Small":  ("0.8rem",  "0.75rem", "1.5rem"),
        "Medium": ("0.9rem",  "0.85rem", "1.75rem"),
        "Large":  ("1.05rem", "0.95rem", "2rem"),
    }
    body, label, metric = size_map.get(get_pref("font_size"), size_map["Medium"])

    st.markdown(f"""
    <style>
        .main p, .main span, .main div {{
            font-size: {body} !important;
        }}
        .info-label, .student-info {{
            font-size: {label} !important;
        }}
        .metric-value {{
            font-size: {metric} !important;
        }}
        {"/* Compact mode */" if get_pref("compact_mode") else ""}
        {".student-card { padding: 0.5rem !important; margin-bottom: 0.4rem !important; }" if get_pref("compact_mode") else ""}
        {".metric-card  { padding: 1rem !important; }" if get_pref("compact_mode") else ""}
    </style>
    """, unsafe_allow_html=True)


def format_date(date_obj) -> str:
    """Format a date object using the user's preferred format."""
    if not date_obj:
        return "—"
    fmt_map = {
        "DD MMM YYYY": "%d %b %Y",
        "DD/MM/YYYY":  "%d/%m/%Y",
        "MM/DD/YYYY":  "%m/%d/%Y",
        "YYYY-MM-DD":  "%Y-%m-%d",
    }
    fmt = fmt_map.get(get_pref("date_format"), "%d %b %Y")
    try:
        return date_obj.strftime(fmt)
    except Exception:
        return str(date_obj)


def render_preferences_panel():
    """
    Render a preferences expander inside the sidebar.
    Call this from sidebar.py.
    """
    init_prefs()

    with st.expander("⚙️ Preferences", expanded=False):

        st.markdown(
            "<p style='font-size:0.75rem; color:#718096; margin-bottom:0.5rem;'>"
            "Settings persist during your session.</p>",
            unsafe_allow_html=True
        )

        # ── Font Size ─────────────────────────────────────
        font = st.select_slider(
            "🔤 Font Size",
            options=FONT_SIZES,
            value=get_pref("font_size"),
            key="pref_font"
        )
        set_pref("font_size", font)

        # ── Items Per Page ────────────────────────────────
        ipp = st.select_slider(
            "📋 Items Per Page",
            options=PAGE_SIZES,
            value=get_pref("items_per_page"),
            key="pref_ipp"
        )
        set_pref("items_per_page", ipp)

        # ── Date Format ───────────────────────────────────
        df = st.selectbox(
            "📅 Date Format",
            options=DATE_FORMATS,
            index=DATE_FORMATS.index(get_pref("date_format")),
            key="pref_date"
        )
        set_pref("date_format", df)

        # ── Default Page ──────────────────────────────────
        dp = st.selectbox(
            "🏠 Default Landing Page",
            options=DEFAULT_PAGES,
            index=DEFAULT_PAGES.index(get_pref("default_page")),
            key="pref_page"
        )
        set_pref("default_page", dp)

        # ── Compact Mode ──────────────────────────────────
        cm = st.toggle(
            "📦 Compact Mode",
            value=get_pref("compact_mode"),
            key="pref_compact"
        )
        set_pref("compact_mode", cm)

        # ── Tooltips ──────────────────────────────────────
        tt = st.toggle(
            "💬 Show Tooltips",
            value=get_pref("show_tooltips"),
            key="pref_tooltips"
        )
        set_pref("show_tooltips", tt)

        # ── Reset button ──────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 Reset to Defaults",
                     use_container_width=True, key="pref_reset"):
            st.session_state["user_prefs"] = dict(DEFAULTS)
            st.rerun()

        st.markdown(f"""
        <p style='font-size:0.7rem; color:#a0aec0; margin-top:0.5rem;
                  text-align:center;'>
            Font: {font} &nbsp;|&nbsp;
            Page: {ipp} items &nbsp;|&nbsp;
            Date: {df}
        </p>
        """, unsafe_allow_html=True)
