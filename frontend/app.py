import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import streamlit as st
from frontend.utils.session_manager import SessionManager
from frontend.utils.api_client import APIClient

# ── ALWAYS FIRST ──────────────────────────────────────────────
st.set_page_config(
    page_title            = "ScholarSense - Login",
    page_icon             = "🎓",
    layout                = "centered",
    initial_sidebar_state = "collapsed"
)

# ── Initialize session (does not restore by default) ────────────
SessionManager.initialize_session()

if SessionManager.is_authenticated():
    st.switch_page("pages/1_📊_Dashboard.py")

# ── OTP state (only once) ──────────────────────────────────────
MAX_ATTEMPTS = 3
if 'login_step'   not in st.session_state:
    st.session_state.login_step   = 'credentials'
if 'otp_user_id'  not in st.session_state:
    st.session_state.otp_user_id  = None
if 'otp_email'    not in st.session_state:
    st.session_state.otp_email    = None
if 'otp_attempts' not in st.session_state:
    st.session_state.otp_attempts = 0


# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Background */
    .main { background-color: #f7fafc; }
    .stApp { background-color: #f7fafc; }

    /* App title */
    .app-title {
        text-align: center;
        color: #1a202c;
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        letter-spacing: -0.5px;
    }
    .app-subtitle {
        text-align: center;
        color: #4a5568;
        font-size: 1.1rem;
        margin-bottom: 2rem;
        font-weight: 500;
    }

    /* Section headers */
    .section-header {
        color: #1a202c;
        font-size: 1.3rem;
        font-weight: 700;
        margin-bottom: 1.5rem;
    }

    /* Input fields */
    .stTextInput > label {
        color: #2d3748 !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
    }
    .stTextInput > div > div > input {
        border: 2px solid #cbd5e0 !important;
        border-radius: 10px !important;
        padding: 0.75rem 1rem !important;
        font-size: 1rem !important;
        color: #1a202c !important;
        background-color: white !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #2563eb !important;
        box-shadow: 0 0 0 3px rgba(37,99,235,0.1) !important;
    }

    /* Primary button */
    .stButton > button[kind="primary"] {
        width: 100%;
        background: #2563eb !important;
        color: white !important;
        border: none !important;
        padding: 0.875rem 1.5rem !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        margin-top: 0.5rem !important;
        transition: all 0.2s !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: #1d4ed8 !important;
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(37,99,235,0.3) !important;
    }

    /* Secondary button */
    .stButton > button[kind="secondary"] {
        width: 100%;
        background: white !important;
        color: #2563eb !important;
        border: 2px solid #2563eb !important;
        padding: 0.75rem 1.5rem !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        margin-top: 0.25rem !important;
    }

    /* OTP info box */
    .otp-info-box {
        background: #eff6ff;
        border: 1px solid #bfdbfe;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 20px;
    }
    .otp-info-box p {
        color: #1e40af;
        margin: 0;
        font-size: 0.95rem;
        font-weight: 500;
    }

    /* OTP digit hint */
    .otp-hint {
        color: #6b7280;
        font-size: 0.85rem;
        text-align: center;
        margin-top: 6px;
    }

    /* Timer badge */
    .timer-badge {
        background: #fef3c7;
        border: 1px solid #fcd34d;
        border-radius: 8px;
        padding: 8px 14px;
        text-align: center;
        color: #92400e;
        font-size: 0.9rem;
        font-weight: 600;
        margin-bottom: 16px;
    }

    /* Back link */
    .back-link {
        text-align: center;
        color: #6b7280;
        font-size: 0.9rem;
        margin-top: 12px;
    }

    /* Footer */
    .footer {
        text-align: center;
        color: #4a5568;
        font-size: 0.9rem;
        margin-top: 3rem;
        padding: 1rem;
    }
    .footer-school {
        font-weight: 600;
        color: #2d3748;
    }

    /* Hide Streamlit branding */
    #MainMenu { visibility: hidden; }
    footer    { visibility: hidden; }
    header    { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ── Already authenticated → redirect ──────────────────────────────────────────
if SessionManager.is_authenticated():
    st.switch_page("pages/1_📊_Dashboard.py")


# ── Check API health ───────────────────────────────────────────────────────────
with st.spinner("Checking system status..."):
    health = APIClient.health_check()
    if health.get('status') != 'healthy':
        st.error("⚠️ **Cannot connect to backend server**")
        st.info("Please ensure the Flask API is running:")
        st.code("python backend/api.py", language="bash")
        st.stop()


# ── Logo + Title (always shown) ────────────────────────────────────────────────
st.markdown('<div style="text-align:center; font-size:4rem;">🎓</div>',
            unsafe_allow_html=True)
st.markdown('<h1 class="app-title">ScholarSense</h1>', unsafe_allow_html=True)
st.markdown('<p class="app-subtitle">AI-Powered Academic Intelligence System</p>',
            unsafe_allow_html=True)


# ==============================================================================
# SCREEN 1 — CREDENTIALS (email + password)
# ==============================================================================

if st.session_state.login_step == 'credentials':

    st.markdown('<div class="section-header">🔐 Login to Continue</div>',
                unsafe_allow_html=True)

    email = st.text_input(
        "📧 Email Address",
        placeholder = "admin@scholarsense.com",
        key         = "login_email"
    )

    password = st.text_input(
        "🔒 Password",
        type        = "password",
        placeholder = "Enter your password",
        key         = "login_password"
    )

    st.write("")  # Spacer
    login_button = st.button(
        "🚀 Login",
        type               = "primary",
        use_container_width = True
    )

    if login_button:
        if not email or not password:
            st.error("❌ Please enter both email and password")
        else:
            with st.spinner("Verifying credentials..."):
                # Call modified login endpoint
                response = APIClient.post(
                    '/api/auth/login',
                    {'email': email, 'password': password},
                    require_auth=False
                )

            if response.get('status') == 'otp_sent':
                # ── Credentials valid → Move to OTP screen ──────────────────
                st.session_state.login_step   = 'otp'
                st.session_state.otp_user_id  = response.get('user_id')
                st.session_state.otp_email    = response.get('email')
                st.session_state.otp_attempts = 0
                st.success("✅ Password verified! OTP sent to your email.")
                st.rerun()

            elif 'error' in response:
                st.error(f"❌ {response['error']}")
            else:
                st.error("❌ Invalid credentials. Please try again.")

    # ── Footer ─────────────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("""
    <div class="footer">
        <p class="footer-school">🏫 Greenwood High School • Academic Year 2025-26</p>
        <p style="margin-top:0.5rem;">Powered by AI • Built for Excellence</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Demo credentials ────────────────────────────────────────────────────────
    with st.expander("🔑 Demo Credentials"):
        st.markdown("""
        **Admin Account:**
        - Email: `admin@scholarsense.com`
        - Password: `admin123`

        **Teacher Account:**
        - Email: `teacher@scholarsense.com`
        - Password: `teacher123`
        """)


# ==============================================================================
# SCREEN 2 — OTP VERIFICATION
# ==============================================================================

elif st.session_state.login_step == 'otp':

    st.markdown('<div class="section-header">📱 Two-Factor Verification</div>',
                unsafe_allow_html=True)

    # ── OTP info box ────────────────────────────────────────────────────────────
    masked_email = st.session_state.otp_email or "your email"
    st.markdown(f"""
    <div class="otp-info-box">
        <p>✅ Password verified successfully!</p>
        <p style="margin-top:8px;">
            📧 OTP sent to: <strong>{masked_email}</strong>
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── Timer notice ────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="timer-badge">
        ⏱️ OTP expires in <strong>5 minutes</strong> •
        Maximum <strong>3 attempts</strong> allowed
    </div>
    """, unsafe_allow_html=True)

    # ── OTP input ───────────────────────────────────────────────────────────────
    otp_input = st.text_input(
        "🔢 Enter 6-Digit OTP",
        placeholder = "e.g. 847392",
        max_chars   = 6,
        key         = "otp_input"
    )
    st.markdown(
        '<p class="otp-hint">Check your registered email inbox</p>',
        unsafe_allow_html=True
    )

    st.write("")  # Spacer

    # ── Action buttons ──────────────────────────────────────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        verify_button = st.button(
            "✅ Verify OTP",
            type               = "primary",
            use_container_width = True
        )

    with col2:
        resend_button = st.button(
            "🔄 Resend OTP",
            type               = "secondary",
            use_container_width = True
        )

    # ── Back to login ───────────────────────────────────────────────────────────
    st.write("")
    back_button = st.button(
        "← Back to Login",
        use_container_width = True
    )

    # ── Handle Verify OTP ───────────────────────────────────────────────────────
    if verify_button:
        if not otp_input:
            st.error("❌ Please enter the OTP")

        elif len(otp_input) != 6 or not otp_input.isdigit():
            st.error("❌ OTP must be exactly 6 digits")

        else:
            with st.spinner("Verifying OTP..."):
                response = APIClient.post(
                    '/api/auth/verify-otp',
                    {
                        'user_id': st.session_state.otp_user_id,
                        'otp'    : otp_input
                    },
                    require_auth=False
                )

            if 'access_token' in response:
                # ── OTP Valid → Store token → Redirect ──────────────────────
                SessionManager.set_session(
                    token = response['access_token'],
                    user  = response['user']
                )

                # Reset OTP state
                st.session_state.login_step   = 'credentials'
                st.session_state.otp_user_id  = None
                st.session_state.otp_email    = None
                st.session_state.otp_attempts = 0

                st.success("✅ Login successful! Redirecting to dashboard...")
                st.rerun()

            elif 'error' in response:
                st.session_state.otp_attempts += 1
                error_msg = response['error']

                if 'locked' in error_msg.lower():
                    st.error(f"🔒 {error_msg}")
                    st.warning(
                        "Your account is temporarily locked. "
                        "Please try again after 15 minutes."
                    )
                    # Reset to credentials screen after lockout
                    st.session_state.login_step  = 'credentials'
                    st.session_state.otp_user_id = None
                    st.session_state.otp_email   = None

                elif 'expired' in error_msg.lower():
                    st.error("⏰ OTP has expired!")
                    st.info("Click **Resend OTP** to get a new one.")

                else:
                    remaining = (MAX_ATTEMPTS - st.session_state.otp_attempts)
                    st.error(f"❌ {error_msg}")

    # ── Handle Resend OTP ───────────────────────────────────────────────────────
    if resend_button:
        with st.spinner("Sending new OTP..."):
            response = APIClient.post(
                '/api/auth/resend-otp',
                {'user_id': st.session_state.otp_user_id},
                require_auth=False
            )

        if response.get('status') == 'otp_sent':
            st.session_state.otp_attempts = 0  # Reset attempts on resend
            st.success(
                f"✅ New OTP sent to {response.get('email', masked_email)}"
            )
            st.info("⏱️ New OTP is valid for 5 minutes.")

        elif 'error' in response:
            st.error(f"❌ {response['error']}")

    # ── Handle Back button ──────────────────────────────────────────────────────
    if back_button:
        st.session_state.login_step   = 'credentials'
        st.session_state.otp_user_id  = None
        st.session_state.otp_email    = None
        st.session_state.otp_attempts = 0
        st.rerun()
