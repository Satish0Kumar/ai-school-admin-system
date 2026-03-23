"""
Session Management for Streamlit - ScholarSense
Uses a local JSON file for reliable session persistence across page refreshes.
Works perfectly for local/development Streamlit apps.
"""
import streamlit as st
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from frontend.utils.api_client import APIClient

# Session file stored in project root (gitignored)
SESSION_FILE = Path(__file__).parent.parent.parent / ".streamlit_session.json"


def _read_session_file() -> dict:
    """Read session data from file"""
    try:
        if SESSION_FILE.exists():
            with open(SESSION_FILE, "r") as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def _write_session_file(data: dict):
    """Write session data to file"""
    try:
        with open(SESSION_FILE, "w") as f:
            json.dump(data, f)
    except Exception:
        pass


def _delete_session_file():
    """Delete session file on logout"""
    try:
        if SESSION_FILE.exists():
            SESSION_FILE.unlink()
    except Exception:
        pass


class SessionManager:

    @staticmethod
    def initialize_session():
        """Set defaults + restore from file if not already in session"""
        # Set defaults only if not present
        for key, val in [
            ('authenticated', False),
            ('user',          None),
            ('token',         None),
            ('token_expiry',  None),
        ]:
            if key not in st.session_state:
                st.session_state[key] = val

        # Already authenticated this run — nothing to do
        if st.session_state.get('authenticated'):
            return

        # ── Restore from session file ──────────────────────────
        data = _read_session_file()
        token  = data.get('token')
        expiry = data.get('expiry')
        user   = data.get('user')

        if token and expiry:
            try:
                expiry_dt = datetime.fromisoformat(expiry)
                if datetime.now() < expiry_dt:
                    # ✅ Valid session — restore it
                    st.session_state.authenticated = True
                    st.session_state.token         = token
                    st.session_state.token_expiry  = expiry_dt
                    st.session_state.user          = user or {}
                else:
                    # Expired — clean up
                    _delete_session_file()
            except Exception:
                _delete_session_file()

    @staticmethod
    def set_session(token: str, user: dict):
        """Called after OTP verify — save to session + file"""
        expiry_dt = datetime.now() + timedelta(hours=8)

        st.session_state.authenticated = True
        st.session_state.token         = token
        st.session_state.user          = user
        st.session_state.token_expiry  = expiry_dt

        _write_session_file({
            'token':  token,
            'expiry': expiry_dt.isoformat(),
            'user':   user
        })

    @staticmethod
    def login(email: str, password: str):
        """Direct login (non-OTP flow)"""
        result = APIClient.login(email, password)
        if 'error' not in result:
            SessionManager.set_session(result['access_token'], result['user'])
            return True
        return result['error']

    @staticmethod
    def logout():
        """Clear session + delete file"""
        st.session_state.authenticated = False
        st.session_state.user          = None
        st.session_state.token         = None
        st.session_state.token_expiry  = None
        _delete_session_file()

    @staticmethod
    def is_authenticated() -> bool:
        if not st.session_state.get('authenticated'):
            return False
        expiry = st.session_state.get('token_expiry')
        if expiry and datetime.now() >= expiry:
            SessionManager.logout()
            return False
        return True

    @staticmethod
    def require_auth():
        """Call at top of every page — restores session or redirects to login"""
        SessionManager.initialize_session()
        if not SessionManager.is_authenticated():
            st.warning("⚠️ Please login to access this page")
            st.switch_page("app.py")
            st.stop()

    @staticmethod
    def get_user():
        return st.session_state.get('user')

    @staticmethod
    def get_token():
        return st.session_state.get('token')

    @staticmethod
    def is_admin():
        user = SessionManager.get_user()
        return user and user.get('role') == 'admin'
