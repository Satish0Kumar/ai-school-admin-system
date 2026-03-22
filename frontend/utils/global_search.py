"""
Global Search — Search across students, incidents, predictions.
"""
import streamlit as st
from frontend.utils.api_client import APIClient


def render_global_search():
    """
    Renders a global search bar with live grouped results.
    Call this on the Dashboard page.
    """
    search_query = st.text_input(
        "🔍 Global Search",
        placeholder="Search students, grades, risk levels...",
        key="global_search_input",
        label_visibility="collapsed"
    )

    if not search_query or len(search_query.strip()) < 2:
        st.markdown(
            "<p style='color:#a0aec0; font-size:0.85rem; margin-top:0.25rem;'>"
            "Type at least 2 characters to search across all students...</p>",
            unsafe_allow_html=True
        )
        return

    query = search_query.strip().lower()

    with st.spinner("Searching..."):
        all_students = APIClient.get_students()

    if not all_students or not isinstance(all_students, list):
        st.warning("⚠️ Could not fetch data for search.")
        return

    # ── Match students ────────────────────────────────────
    matched = []
    for s in all_students:
        full_name  = f"{s.get('first_name','')} {s.get('last_name','')}".lower()
        student_id = str(s.get('student_id', '')).lower()
        grade      = str(s.get('grade', '')).lower()
        parent     = str(s.get('parent_name', '')).lower()
        gender     = str(s.get('gender', '')).lower()

        if any(query in field for field in
               [full_name, student_id, grade, parent, gender]):
            matched.append(s)

    # ── Render results ────────────────────────────────────
    total = len(matched)

    st.markdown(f"""
    <div style="background:#ebf8ff; border:1px solid #bee3f8;
                border-radius:8px; padding:0.5rem 1rem;
                margin:0.5rem 0; font-size:0.875rem; color:#2c5282;">
        🔍 Found <strong>{total}</strong> result(s) for
        "<strong>{search_query}</strong>"
    </div>
    """, unsafe_allow_html=True)

    if not matched:
        st.markdown("""
        <div style="text-align:center; padding:1.5rem; color:#a0aec0;">
            <span style="font-size:1.5rem;">😕</span><br>
            No results found. Try a different name, ID, or grade.
        </div>
        """, unsafe_allow_html=True)
        return

    # ── Group by grade ────────────────────────────────────
    grade_groups = {}
    for s in matched:
        g = str(s.get('grade', 'Unknown'))
        grade_groups.setdefault(g, []).append(s)

    for grade, group in sorted(grade_groups.items()):
        st.markdown(f"""
        <div style="background:#f7fafc; border-left:4px solid #3b82f6;
                    padding:0.4rem 0.75rem; margin:0.75rem 0 0.4rem 0;
                    border-radius:0 6px 6px 0;">
            <span style="font-weight:700; color:#1e40af;
                         font-size:0.85rem;">📚 Grade {grade}
            </span>
            <span style="color:#718096; font-size:0.8rem;">
                &nbsp;— {len(group)} student(s)
            </span>
        </div>
        """, unsafe_allow_html=True)

        for s in group:
            status = "🟢" if s.get('is_active', True) else "🔴"
            c1, c2, c3, c4 = st.columns([3, 2, 2, 1])
            with c1:
                st.markdown(
                    f"**{s['first_name']} {s['last_name']}**  "
                    f"<span style='color:#718096; font-size:0.85rem;'>"
                    f"ID: {s['student_id']}</span>",
                    unsafe_allow_html=True
                )
            with c2:
                st.markdown(
                    f"<span style='color:#4a5568; font-size:0.875rem;'>"
                    f"👤 {s.get('gender','N/A')} &nbsp;|&nbsp; "
                    f"Age {s.get('age','N/A')}</span>",
                    unsafe_allow_html=True
                )
            with c3:
                st.markdown(
                    f"<span style='color:#4a5568; font-size:0.875rem;'>"
                    f"{status} {s.get('parent_name','N/A')}</span>",
                    unsafe_allow_html=True
                )
            with c4:
                if st.button("View", key=f"gs_view_{s['id']}",
                             use_container_width=True):
                    st.session_state['selected_student_id'] = s['id']
                    st.switch_page("pages/3_👤_Student_Profile.py")

            st.markdown(
                "<hr style='margin:0.3rem 0; border-color:#f0f4f8;'>",
                unsafe_allow_html=True
            )
