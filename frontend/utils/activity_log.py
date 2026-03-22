"""
Activity Log — Tracks recent user actions across the app.
Stored in session_state so it persists during the session.
"""
import streamlit as st
from datetime import datetime


MAX_ACTIVITIES = 50  # keep last 50 actions


def log_activity(action: str, entity: str = "", icon: str = "📌", level: str = "info"):
    """
    Log an activity to the session feed.
    level: 'info' | 'success' | 'warning' | 'danger'
    """
    if 'activity_feed' not in st.session_state:
        st.session_state['activity_feed'] = []

    entry = {
        "time":   datetime.now().strftime("%H:%M:%S"),
        "date":   datetime.now().strftime("%d %b"),
        "action": action,
        "entity": entity,
        "icon":   icon,
        "level":  level,
    }

    st.session_state['activity_feed'].insert(0, entry)

    # Cap at MAX_ACTIVITIES
    st.session_state['activity_feed'] = \
        st.session_state['activity_feed'][:MAX_ACTIVITIES]


def get_activities(limit: int = 10):
    """Return recent activities"""
    return st.session_state.get('activity_feed', [])[:limit]


def render_activity_feed(limit: int = 8):
    """Render a styled activity timeline"""
    activities = get_activities(limit)

    level_colors = {
        'info':    ('#ebf8ff', '#3182ce', '#bee3f8'),
        'success': ('#f0fff4', '#38a169', '#c6f6d5'),
        'warning': ('#fffaf0', '#dd6b20', '#feebc8'),
        'danger':  ('#fff5f5', '#e53e3e', '#fed7d7'),
    }

    if not activities:
        st.markdown("""
        <div style="text-align:center; padding:2rem; color:#a0aec0;">
            <span style="font-size:2rem;">📭</span><br>
            <span style="font-size:0.9rem;">No recent activity yet.<br>
            Actions you take will appear here.</span>
        </div>
        """, unsafe_allow_html=True)
        return

    for act in activities:
        bg, text, border = level_colors.get(act['level'], level_colors['info'])
        st.markdown(f"""
        <div style="display:flex; align-items:flex-start; gap:0.75rem;
                    background:{bg}; border-left:4px solid {border};
                    border-radius:8px; padding:0.65rem 1rem;
                    margin-bottom:0.5rem;">
            <span style="font-size:1.2rem; margin-top:2px;">{act['icon']}</span>
            <div style="flex:1;">
                <div style="font-weight:700; color:{text};
                            font-size:0.875rem;">{act['action']}</div>
                <div style="color:#718096; font-size:0.775rem;
                            margin-top:2px;">{act['entity']}</div>
            </div>
            <div style="color:#a0aec0; font-size:0.75rem;
                        white-space:nowrap;">{act['date']} {act['time']}</div>
        </div>
        """, unsafe_allow_html=True)
