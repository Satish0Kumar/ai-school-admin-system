import streamlit as st
import requests
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="User Management - ScholarSense",
    page_icon="👤",
    layout="wide"
)


from frontend.utils.sidebar import render_sidebar
render_sidebar()


API_BASE = "http://localhost:5000"

# ─────────────────────────────────────────────
# Session / Auth helpers
# ─────────────────────────────────────────────
def get_headers():
    token = (
        st.session_state.get("token") or
        st.session_state.get("access_token") or
        ""
    )
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

def is_logged_in():
    return st.session_state.get("authenticated", False) or \
           st.session_state.get("token") is not None

def is_admin():
    role = st.session_state.get("user", {}).get("role", "")
    return role.lower() == "admin"


# ─────────────────────────────────────────────
# API calls
# ─────────────────────────────────────────────
def get_all_users():
    try:
        res = requests.get(f"{API_BASE}/api/users", headers=get_headers(), timeout=5)
        if res.status_code == 200:
            return res.json(), None
        return [], res.json().get("message", "Failed to fetch users")
    except Exception as e:
        return [], str(e)

def create_user(name, email, password, role):
    try:
        payload = {"name": name, "email": email, "password": password, "role": role}
        res = requests.post(f"{API_BASE}/api/users/create", json=payload, headers=get_headers(), timeout=5)
        return res.status_code in [200, 201], res.json().get("message", "Done")
    except Exception as e:
        return False, str(e)

def delete_user(user_id):
    try:
        res = requests.delete(f"{API_BASE}/api/users/{user_id}", headers=get_headers(), timeout=5)
        return res.status_code == 200, res.json().get("message", "Done")
    except Exception as e:
        return False, str(e)

def toggle_user_status(user_id, active):
    try:
        payload = {"is_active": not active}
        res = requests.put(f"{API_BASE}/api/users/{user_id}", json=payload, headers=get_headers(), timeout=5)
        return res.status_code == 200, res.json().get("message", "Done")
    except Exception as e:
        return False, str(e)

# ─────────────────────────────────────────────
# Auth Guard
# ─────────────────────────────────────────────
if not is_logged_in():
    st.warning("⚠️ Please login first!")
    st.page_link("app.py", label="Go to Login", icon="🔐")
    st.stop()

if not is_admin():
    st.error("🚫 Access Denied! This page is for Admins only.")
    st.stop()

# ─────────────────────────────────────────────
# Page Header
# ─────────────────────────────────────────────
st.title("👤 User Management")
st.markdown("Manage teachers, admins and staff accounts in **ScholarSense**.")
st.divider()

# ─────────────────────────────────────────────
# Fetch Users
# ─────────────────────────────────────────────
users, err = get_all_users()

# ─────────────────────────────────────────────
# Stats Row
# ─────────────────────────────────────────────
total    = len(users)
admins   = sum(1 for u in users if u.get("role") == "admin")
teachers = sum(1 for u in users if u.get("role") == "teacher")
active   = sum(1 for u in users if u.get("is_active", True))

col1, col2, col3, col4 = st.columns(4)
col1.metric("👥 Total Users",    total)
col2.metric("🔑 Admins",         admins)
col3.metric("🏫 Teachers",       teachers)
col4.metric("✅ Active",         active)

st.divider()

# ─────────────────────────────────────────────
# Tabs
# ─────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📋 All Users", "➕ Add Teacher", "🔑 Add Admin"])

# ══════════════════════════════════════════════
# TAB 1 — All Users Table
# ══════════════════════════════════════════════
with tab1:
    st.subheader("📋 All Registered Users")

    if err:
        st.error(f"❌ {err}")
    elif not users:
        st.info("No users found.")
    else:
        # Search & Filter
        col_s, col_f = st.columns([3, 1])
        search = col_s.text_input("🔍 Search by name or email", placeholder="Type name or email...")
        role_filter = col_f.selectbox("Filter by Role", ["All", "admin", "teacher"])

        filtered = users
        if search:
            filtered = [u for u in filtered if
                        search.lower() in u.get("name", "").lower() or
                        search.lower() in u.get("email", "").lower()]
        if role_filter != "All":
            filtered = [u for u in filtered if u.get("role") == role_filter]

        st.markdown(f"**Showing {len(filtered)} of {total} users**")
        st.markdown("")

        # User Cards Table
        for user in filtered:
            with st.container(border=True):
                c1, c2, c3, c4, c5 = st.columns([3, 2, 1, 1, 1])

                role_badge = "🔑 Admin" if user.get("role") == "admin" else "🏫 Teacher"
                status     = "🟢 Active" if user.get("is_active", True) else "🔴 Inactive"

                name = user.get('full_name') or user.get('name') or user.get('username') or 'N/A'
                c1.markdown(f"**{name}**  \n📧 {user.get('email', 'N/A')}")

                c2.markdown(f"{role_badge}  \n{status}")
                c3.markdown(f"**ID**  \n`{user.get('id', 'N/A')}`")

                uid    = user.get("id")
                active = user.get("is_active", True)

                # Deactivate / Activate button
                btn_label = "🔴 Deactivate" if active else "🟢 Activate"
                if c4.button(btn_label, key=f"toggle_{uid}", use_container_width=True):
                    ok, msg = toggle_user_status(uid, active)
                    if ok:
                        st.success(f"✅ {msg}")
                        st.rerun()
                    else:
                        st.error(f"❌ {msg}")

                # Delete button — prevent self-delete
                current_user_id = st.session_state.get("user_id")
                if uid != current_user_id:
                    if c5.button("🗑️ Delete", key=f"del_{uid}", use_container_width=True):
                        st.session_state[f"confirm_delete_{uid}"] = True

                # Confirm delete
                if st.session_state.get(f"confirm_delete_{uid}"):
                    st.warning(f"⚠️ Are you sure you want to delete **{user.get('name')}**?")
                    y, n = st.columns(2)
                    if y.button("✅ Yes, Delete", key=f"yes_{uid}"):
                        ok, msg = delete_user(uid)
                        if ok:
                            st.success("✅ User deleted!")
                            del st.session_state[f"confirm_delete_{uid}"]
                            st.rerun()
                        else:
                            st.error(f"❌ {msg}")
                    if n.button("❌ Cancel", key=f"no_{uid}"):
                        del st.session_state[f"confirm_delete_{uid}"]
                        st.rerun()

# ══════════════════════════════════════════════
# TAB 2 — Add Teacher
# ══════════════════════════════════════════════
with tab2:
    st.subheader("➕ Add New Teacher")
    st.markdown("Create a new **Teacher** account. Teacher can view students, add marks, log incidents.")
    st.markdown("")

    with st.form("add_teacher_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        t_name  = col1.text_input("👤 Full Name*",        placeholder="e.g. Ramesh Kumar")
        t_email = col2.text_input("📧 Email Address*",    placeholder="e.g. ramesh@school.com")
        col3, col4 = st.columns(2)
        t_pass  = col3.text_input("🔑 Password*",         placeholder="Min 6 characters", type="password")
        t_pass2 = col4.text_input("🔑 Confirm Password*", placeholder="Re-enter password", type="password")

        st.markdown("**Permissions for Teacher role:**")
        st.markdown("✅ View Students &nbsp;&nbsp; ✅ Add Marks &nbsp;&nbsp; ✅ Log Incidents &nbsp;&nbsp; ✅ View Reports &nbsp;&nbsp; ❌ Manage Users")

        submitted = st.form_submit_button("➕ Create Teacher Account", use_container_width=True, type="primary")

        if submitted:
            if not t_name or not t_email or not t_pass:
                st.error("❌ All fields are required!")
            elif t_pass != t_pass2:
                st.error("❌ Passwords do not match!")
            elif len(t_pass) < 6:
                st.error("❌ Password must be at least 6 characters!")
            elif "@" not in t_email:
                st.error("❌ Enter a valid email address!")
            else:
                with st.spinner("Creating teacher account..."):
                    ok, msg = create_user(t_name, t_email, t_pass, "teacher")
                if ok:
                    st.success(f"✅ Teacher **{t_name}** created successfully!")
                    st.balloons()
                else:
                    st.error(f"❌ {msg}")

# ══════════════════════════════════════════════
# TAB 3 — Add Admin
# ══════════════════════════════════════════════
with tab3:
    st.subheader("🔑 Add New Admin")
    st.markdown("Create a new **Admin** account. Admin has full access to all modules.")
    st.markdown("")

    st.warning("⚠️ **Caution:** Admin accounts have full access including User Management, Delete operations, and System Settings. Only create admin accounts for trusted staff.")

    with st.form("add_admin_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        a_name  = col1.text_input("👤 Full Name*",        placeholder="e.g. Priya Sharma")
        a_email = col2.text_input("📧 Email Address*",    placeholder="e.g. priya@school.com")
        col3, col4 = st.columns(2)
        a_pass  = col3.text_input("🔑 Password*",         placeholder="Min 8 characters", type="password")
        a_pass2 = col4.text_input("🔑 Confirm Password*", placeholder="Re-enter password", type="password")

        st.markdown("**Permissions for Admin role:**")
        st.markdown("✅ View Students &nbsp;&nbsp; ✅ Add Marks &nbsp;&nbsp; ✅ Log Incidents &nbsp;&nbsp; ✅ View Reports &nbsp;&nbsp; ✅ Manage Users &nbsp;&nbsp; ✅ Full Access")

        confirm = st.checkbox("✅ I confirm creating a new Admin account")
        submitted_a = st.form_submit_button("🔑 Create Admin Account", use_container_width=True, type="primary")

        if submitted_a:
            if not confirm:
                st.error("❌ Please check the confirmation box!")
            elif not a_name or not a_email or not a_pass:
                st.error("❌ All fields are required!")
            elif a_pass != a_pass2:
                st.error("❌ Passwords do not match!")
            elif len(a_pass) < 8:
                st.error("❌ Admin password must be at least 8 characters!")
            elif "@" not in a_email:
                st.error("❌ Enter a valid email address!")
            else:
                with st.spinner("Creating admin account..."):
                    ok, msg = create_user(a_name, a_email, a_pass, "admin")
                if ok:
                    st.success(f"✅ Admin **{a_name}** created successfully!")
                    st.balloons()
                else:
                    st.error(f"❌ {msg}")
