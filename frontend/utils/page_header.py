"""
ScholarSense - Shared Page Header Component
Provides consistent header + breadcrumb across all pages
"""
import streamlit as st
from datetime import datetime

def render_page_header(
    title: str,
    subtitle: str = "",
    icon: str = "",
    section: str = "",
    show_time: bool = True
):
    """
    Renders a consistent page header with breadcrumb.

    Usage:
        render_page_header(
            title    = "Dashboard",
            subtitle = "School-wide overview and key metrics",
            icon     = "📊",
            section  = "Overview"
        )
    """

    # ── Breadcrumb ─────────────────────────────────────────
    if section:
        st.markdown(
            f"<p style='color:#6b7280; font-size:0.82rem; margin-bottom:4px;'>"
            f"🏠 Home &nbsp;›&nbsp; {section} &nbsp;›&nbsp; <b>{title}</b></p>",
            unsafe_allow_html=True
        )

    # ── Title Row ──────────────────────────────────────────
    col1, col2 = st.columns([4, 1])

    with col1:
        full_title = f"{icon} {title}" if icon else title
        st.title(full_title)
        if subtitle:
            st.caption(subtitle)

    with col2:
        if show_time:
            now = datetime.now().strftime("%d %b %Y, %I:%M %p")
            st.markdown(
                f"<div style='text-align:right; padding-top:16px;'>"
                f"<span style='background:#f0f4ff; border:1px solid #dbeafe; "
                f"border-radius:8px; padding:6px 12px; font-size:0.8rem; color:#1e40af;'>"
                f"🕐 {now}</span></div>",
                unsafe_allow_html=True
            )

    st.divider()
