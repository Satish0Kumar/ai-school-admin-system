"""
UI Helper Utilities
ScholarSense - Reusable loading states and skeleton screens
"""
import streamlit as st
from typing import Callable, Any, Optional



def show_skeleton_cards(count=3, cols=3):
    """Show animated placeholder cards while data loads"""
    st.markdown("""
    <style>
        @keyframes shimmer {
            0%   { background-position: -1000px 0; }
            100% { background-position: 1000px 0; }
        }
        .skeleton {
            background: linear-gradient(
                90deg,
                #f0f4f8 25%,
                #e2e8f0 50%,
                #f0f4f8 75%
            );
            background-size: 1000px 100%;
            animation: shimmer 1.5s infinite;
            border-radius: 8px;
            margin-bottom: 0.5rem;
        }
        .skeleton-card {
            background: white;
            padding: 1.2rem;
            border-radius: 12px;
            border: 1px solid #e2e8f0;
            margin-bottom: 1rem;
        }
    </style>
    """, unsafe_allow_html=True)

    columns = st.columns(cols)
    for i in range(count):
        with columns[i % cols]:
            st.markdown("""
            <div class="skeleton-card">
                <div class="skeleton" style="height:16px; width:60%;"></div>
                <div class="skeleton" style="height:36px; width:40%; margin-top:0.8rem;"></div>
                <div class="skeleton" style="height:12px; width:80%; margin-top:0.8rem;"></div>
            </div>
            """, unsafe_allow_html=True)


def show_skeleton_table(rows=5):
    """Show animated placeholder rows while table data loads"""
    st.markdown("""
    <style>
        .skeleton-row {
            display: flex; gap: 1rem;
            padding: 0.6rem 0;
            border-bottom: 1px solid #f0f4f8;
        }
    </style>
    """, unsafe_allow_html=True)

    for _ in range(rows):
        st.markdown("""
        <div class="skeleton-row">
            <div class="skeleton" style="height:14px; width:20%; border-radius:6px;"></div>
            <div class="skeleton" style="height:14px; width:15%; border-radius:6px;"></div>
            <div class="skeleton" style="height:14px; width:15%; border-radius:6px;"></div>
            <div class="skeleton" style="height:14px; width:30%; border-radius:6px;"></div>
            <div class="skeleton" style="height:14px; width:10%; border-radius:6px;"></div>
        </div>
        """, unsafe_allow_html=True)


def show_loading_banner(message="Loading data, please wait..."):
    """Show a styled top banner while fetching"""
    st.markdown(f"""
    <div style="background: linear-gradient(90deg, #2563eb, #1d4ed8);
                color: white; padding: 0.75rem 1.5rem;
                border-radius: 10px; margin-bottom: 1rem;
                display: flex; align-items: center; gap: 0.75rem;
                box-shadow: 0 4px 12px rgba(37,99,235,0.3);">
        <span style="font-size:1.2rem;">⏳</span>
        <span style="font-weight:600;">{message}</span>
    </div>
    """, unsafe_allow_html=True)


def show_error_state(message="Something went wrong.", retry_label="🔄 Retry"):
    """Show a friendly error card with optional retry button"""
    st.markdown(f"""
    <div style="background:#fff5f5; border:2px solid #fc8181;
                border-radius:12px; padding:1.5rem 2rem;
                margin:1rem 0; text-align:center;">
        <p style="font-size:2rem; margin:0;">❌</p>
        <p style="color:#c53030; font-weight:700;
                  font-size:1.1rem; margin:0.5rem 0;">{message}</p>
        <p style="color:#742a2a; font-size:0.9rem; margin:0;">
            Please check your connection or try again.
        </p>
    </div>
    """, unsafe_allow_html=True)
    return st.button(retry_label, use_container_width=False)


def show_empty_state(title="No data found",
                     subtitle="Try adjusting your filters or add new records.",
                     icon="📭"):
    """Show a friendly empty state card"""
    st.markdown(f"""
    <div style="background:white; border:2px dashed #cbd5e0;
                border-radius:16px; padding:3rem 2rem;
                margin:1rem 0; text-align:center;">
        <p style="font-size:3rem; margin:0;">{icon}</p>
        <p style="color:#1a202c; font-weight:700;
                  font-size:1.2rem; margin:0.75rem 0 0.25rem 0;">{title}</p>
        <p style="color:#718096; font-size:0.95rem; margin:0;">{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)


def safe_api_call(fn, *args, fallback=None, error_msg="Failed to load data.", **kwargs):
    """
    Safely call any API function.
    Returns result on success, fallback value on failure.
    Shows error message automatically.
    """
    try:
        result = fn(*args, **kwargs)
        if isinstance(result, dict) and result.get('error'):
            st.warning(f"⚠️ {result['error']}")
            return fallback
        return result
    except Exception as e:
        st.error(f"❌ {error_msg} ({str(e)})")
        return fallback if fallback is not None else []


def show_toast(message, type="success", duration=3):
    """
    Show an auto-dismissing toast notification.
    type: 'success' | 'error' | 'warning' | 'info'
    """
    colors = {
        'success': ('#f0fff4', '#276749', '#38a169', '✅'),
        'error':   ('#fff5f5', '#742a2a', '#e53e3e', '❌'),
        'warning': ('#fffaf0', '#7c2d12', '#dd6b20', '⚠️'),
        'info':    ('#ebf8ff', '#2c5282', '#3182ce', 'ℹ️'),
    }
    bg, text_color, border_color, icon = colors.get(type, colors['info'])

    toast_id = f"toast_{id(message)}"

    st.markdown(f"""
    <style>
        #{toast_id} {{
            animation: fadeOut 0.5s ease {duration}s forwards;
        }}
        @keyframes fadeOut {{
            from {{ opacity: 1; transform: translateY(0); }}
            to   {{ opacity: 0; transform: translateY(-10px); pointer-events: none; }}
        }}
    </style>
    <div id="{toast_id}"
         style="background:{bg}; border:2px solid {border_color};
                border-radius:10px; padding:0.75rem 1.25rem;
                margin-bottom:0.75rem; display:flex;
                align-items:center; gap:0.75rem;
                box-shadow: 0 4px 12px rgba(0,0,0,0.08);">
        <span style="font-size:1.2rem;">{icon}</span>
        <span style="color:{text_color}; font-weight:600;
                     font-size:0.95rem;">{message}</span>
    </div>
    """, unsafe_allow_html=True)


def show_action_result(result, success_msg, error_key='error'):
    """
    Check API result dict and show toast accordingly.
    Returns True if success, False if error.
    """
    if result and error_key not in result:
        show_toast(success_msg, type='success')
        return True
    else:
        err = result.get(error_key, 'Unknown error') if result else 'No response'
        show_toast(f"Failed: {err}", type='error')
        return False


def inject_keyboard_shortcuts():
    """
    Inject JS for keyboard shortcuts:
    - Press '/' → focus the search input
    - Press 'Escape' → blur/unfocus any input
    """
    st.markdown("""
    <script>
    document.addEventListener('keydown', function(e) {
        // '/' to focus search
        if (e.key === '/' && document.activeElement.tagName !== 'INPUT'
                          && document.activeElement.tagName !== 'TEXTAREA') {
            e.preventDefault();
            const inputs = document.querySelectorAll('input[type="text"]');
            if (inputs.length > 0) inputs[0].focus();
        }
        // 'Escape' to blur
        if (e.key === 'Escape') {
            document.activeElement.blur();
        }
    });
    </script>
    """, unsafe_allow_html=True)


def show_shortcut_hints():
    """Show small keyboard shortcut pills at the bottom of sidebar"""
    st.markdown("""
    <div style="margin-top:1rem; padding:0.75rem 1rem;
                background:#f7fafc; border-radius:10px;
                border:1px solid #e2e8f0;">
        <p style="margin:0 0 0.5rem 0; font-size:0.75rem;
                  font-weight:700; color:#4a5568;
                  text-transform:uppercase; letter-spacing:0.05em;">
            ⌨️ Shortcuts
        </p>
        <p style="margin:0.2rem 0; font-size:0.8rem; color:#718096;">
            <kbd style="background:#e2e8f0; padding:1px 6px;
                        border-radius:4px; font-size:0.75rem;">/</kbd>
            &nbsp; Focus search
        </p>
        <p style="margin:0.2rem 0; font-size:0.8rem; color:#718096;">
            <kbd style="background:#e2e8f0; padding:1px 6px;
                        border-radius:4px; font-size:0.75rem;">Esc</kbd>
            &nbsp; Clear focus
        </p>
        <p style="margin:0.2rem 0; font-size:0.8rem; color:#718096;">
            <kbd style="background:#e2e8f0; padding:1px 6px;
                        border-radius:4px; font-size:0.75rem;">R</kbd>
            &nbsp; Refresh page
        </p>
    </div>
    """, unsafe_allow_html=True)



def confirm_dialog(action_label, key, warning_msg=None):
    """
    Shows an inline confirmation widget.
    Returns True only when user clicks the confirm button.

    Usage:
        if confirm_dialog("Delete Student", key="del_s_123"):
            # do the delete
    """
    confirm_key  = f"confirm_{key}"
    trigger_key  = f"trigger_{key}"

    # Step 1 — Show the danger button
    if not st.session_state.get(trigger_key, False):
        if st.button(f"🗑️ {action_label}", key=f"btn_{key}",
                     type="secondary", use_container_width=True):
            st.session_state[trigger_key] = True
            st.rerun()
        return False

    # Step 2 — Show confirmation box
    st.markdown(f"""
    <div style="background:#fff5f5; border:2px solid #fc8181;
                border-radius:10px; padding:1rem; margin:0.5rem 0;">
        <p style="color:#c53030; font-weight:700; margin:0 0 0.5rem 0;">
            ⚠️ Are you sure?
        </p>
        <p style="color:#742a2a; font-size:0.875rem; margin:0;">
            {warning_msg or f"This will permanently {action_label.lower()}. This cannot be undone."}
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Yes, proceed", key=f"yes_{key}",
                     type="primary", use_container_width=True):
            st.session_state[trigger_key]  = False
            st.session_state[confirm_key]  = True
            return True
    with col2:
        if st.button("❌ Cancel", key=f"no_{key}",
                     use_container_width=True):
            st.session_state[trigger_key] = False
            st.rerun()

    return False


def bulk_action_bar(selected_ids, actions):
    """
    Show a sticky bulk-action bar when items are selected.
    actions: list of dicts → [{"label": "🗑️ Delete", "key": "bulk_delete", "type": "primary"}]
    Returns the key of the action clicked, or None.
    """
    if not selected_ids:
        return None

    st.markdown(f"""
    <div style="background:#1a202c; color:white; padding:0.75rem 1.25rem;
                border-radius:10px; margin-bottom:1rem;
                display:flex; align-items:center; gap:1rem;">
        <span style="font-weight:700; font-size:0.95rem;">
            ✅ {len(selected_ids)} student(s) selected
        </span>
    </div>
    """, unsafe_allow_html=True)

    cols = st.columns(len(actions) + 1)
    for i, action in enumerate(actions):
        with cols[i]:
            if st.button(action["label"], key=action["key"],
                         type=action.get("type", "secondary"),
                         use_container_width=True):
                return action["key"]
    with cols[-1]:
        if st.button("✖️ Clear Selection", key="bulk_clear",
                     use_container_width=True):
            return "clear"
    return None


def inject_theme_css():
    """
    Inject light or dark mode CSS based on session_state['dark_mode'].
    Call this on EVERY page right after render_sidebar().
    """
    dark = st.session_state.get('dark_mode', False)

    if dark:
        theme = """
        <style>
            /* ── Dark Mode ── */
            .stApp, [data-testid="stAppViewContainer"] {
                background-color: #0f172a !important; color: #e2e8f0 !important;
            }
            [data-testid="stSidebar"] {
                background-color: #1e293b !important;
                border-right: 1px solid #334155 !important;
            }
            .main { background-color: #0f172a !important; }
            div[data-testid="stMetric"] {
                background: #1e293b !important;
                border: 1px solid #334155 !important;
                border-radius: 10px; padding: 1rem;
            }
            .stDataFrame, [data-testid="stTable"] {
                background: #1e293b !important; color: #e2e8f0 !important;
            }
            .stTextInput input, .stSelectbox select, .stTextArea textarea {
                background: #1e293b !important; color: #e2e8f0 !important;
                border-color: #475569 !important;
            }
            .student-card, .info-box, .incident-card {
                background: #1e293b !important;
                border-color: #334155 !important;
                color: #e2e8f0 !important;
            }
            .student-name, .info-value { color: #f1f5f9 !important; }
            .student-info, .info-label { color: #94a3b8 !important; }
            h1, h2, h3, h4, p, span, label { color: #e2e8f0 !important; }
            .stButton > button {
                background: #1e293b !important;
                color: #e2e8f0 !important;
                border-color: #475569 !important;
            }
            .stButton > button[kind="primary"] {
                background: #3b82f6 !important;
                color: white !important;
            }
            [data-testid="stExpander"] {
                background: #1e293b !important;
                border-color: #334155 !important;
            }
            hr { border-color: #334155 !important; }
        </style>
        """
    else:
        theme = """
        <style>
            /* ── Light Mode (default) ── */
            .stApp { background-color: #f7fafc !important; }
        </style>
        """

    st.markdown(theme, unsafe_allow_html=True)
    inject_responsive_css()
    # Apply font size preference
    from frontend.utils.preferences import apply_font_size, init_prefs
    init_prefs()
    apply_font_size()



def inject_responsive_css():
    """
    Inject mobile-responsive CSS.
    Stacks columns, adjusts font sizes, fixes sidebar on small screens.
    Call once per page inside inject_theme_css() or separately.
    """
    st.markdown("""
    <style>
        /* ── Responsive Breakpoints ── */

        /* Tablet & below (≤768px) */
        @media (max-width: 768px) {

            /* Stack all columns vertically */
            [data-testid="column"] {
                width: 100% !important;
                flex: 1 1 100% !important;
                min-width: 100% !important;
            }

            /* Reduce main padding */
            .main { padding: 0.5rem 0.75rem !important; }

            /* Smaller titles */
            h1 { font-size: 1.4rem !important; }
            h2 { font-size: 1.2rem !important; }
            h3 { font-size: 1rem !important; }

            /* Metric cards full width */
            .metric-card {
                padding: 1rem !important;
                margin-bottom: 0.5rem;
            }
            .metric-value { font-size: 2rem !important; }

            /* Student cards */
            .student-card { padding: 0.75rem !important; }
            .student-name { font-size: 0.95rem !important; }

            /* Shrink buttons */
            .stButton > button {
                font-size: 0.8rem !important;
                padding: 0.4rem 0.6rem !important;
            }

            /* Fix tables overflow */
            [data-testid="stDataFrame"] {
                overflow-x: auto !important;
            }

            /* Hide sidebar by default on mobile */
            [data-testid="stSidebar"] {
                transform: translateX(-100%);
                transition: transform 0.3s ease;
            }
            [data-testid="stSidebar"][aria-expanded="true"] {
                transform: translateX(0);
            }
        }

        /* Small phones (≤480px) */
        @media (max-width: 480px) {
            h1 { font-size: 1.2rem !important; }
            .metric-value { font-size: 1.6rem !important; }
            .metric-label { font-size: 0.75rem !important; }

            /* Single column tabs */
            [data-testid="stTabs"] button {
                font-size: 0.75rem !important;
                padding: 0.3rem 0.5rem !important;
            }

            /* Compact expanders */
            [data-testid="stExpander"] summary {
                font-size: 0.85rem !important;
            }
        }

        /* Desktop (≥1200px) — enhance wide layout */
        @media (min-width: 1200px) {
            .main { padding: 1rem 3rem !important; }
            .metric-value { font-size: 3rem !important; }
        }
    </style>
    """, unsafe_allow_html=True)


def responsive_columns(desktop_spec, mobile_cols=1):
    """
    Returns st.columns() but with mobile-aware hint.
    Usage: cols = responsive_columns([3, 1, 1])
    On desktop → 3 columns as specified.
    On mobile  → CSS handles stacking automatically.
    """
    return st.columns(desktop_spec)
