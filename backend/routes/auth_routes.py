# backend/routes/auth_routes.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token, get_jwt
from datetime import timedelta

from backend.auth.auth_service import AuthService
from backend.services.otp_service import OtpService
from backend.services.email_service import EmailService

auth_bp = Blueprint('auth', __name__)


# ============================================
# POST /api/auth/login
# ============================================
@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        email    = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400

        result = AuthService.login(email, password)
        if not result:
            print(f"❌ Login failed: {email}")
            return jsonify({'error': 'Invalid credentials'}), 401

        user    = result['user']
        user_id = user['id']

        otp_data = OtpService.create_otp(user_id)
        if 'error' in otp_data:
            return jsonify({'error': 'Failed to generate OTP'}), 500

        email_result = EmailService.send_otp_email(
            to_email  = user['email'],
            user_name = user['full_name'],
            otp_code  = otp_data['otp_code']
        )
        if email_result['status'] == 'failed':
            return jsonify({'error': 'Failed to send OTP email'}), 500

        masked_email = OtpService.mask_email(user['email'])
        print(f"✅ OTP sent to {user['email']} for user {user_id}")

        return jsonify({
            'status' : 'otp_sent',
            'message': f'OTP sent to {masked_email}',
            'user_id': user_id,
            'email'  : masked_email
        }), 200

    except Exception as e:
        print(f"❌ Login error: {e}")
        return jsonify({'error': 'Internal server error'}), 500


# ============================================
# POST /api/auth/verify-otp
# ============================================
@auth_bp.route('/api/auth/verify-otp', methods=['POST'])
def verify_otp():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        user_id     = data.get('user_id')
        entered_otp = data.get('otp', '').strip()

        if not user_id or not entered_otp:
            return jsonify({'error': 'user_id and otp are required'}), 400

        if len(entered_otp) != 6 or not entered_otp.isdigit():
            return jsonify({'error': 'OTP must be exactly 6 digits'}), 400

        verify_result = OtpService.verify_otp(user_id, entered_otp)

        if verify_result['status'] == 'locked':
            return jsonify({'error': verify_result['message']}), 429
        if verify_result['status'] == 'expired':
            return jsonify({'error': verify_result['message']}), 401
        if verify_result['status'] == 'invalid':
            return jsonify({
                'error'    : verify_result['message'],
                'remaining': verify_result.get('remaining', 0)
            }), 401
        if verify_result['status'] == 'error':
            return jsonify({'error': verify_result['message']}), 500

        token_result = AuthService.generate_token_for_user(user_id)
        if not token_result:
            return jsonify({'error': 'Failed to generate token'}), 500

        print(f"✅ 2FA login complete for user {user_id}")
        return jsonify(token_result), 200

    except Exception as e:
        print(f"❌ OTP verify error: {e}")
        return jsonify({'error': 'Internal server error'}), 500


# ============================================
# POST /api/auth/resend-otp
# ============================================
@auth_bp.route('/api/auth/resend-otp', methods=['POST'])
def resend_otp():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        user_id = data.get('user_id')
        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400

        user = AuthService.get_user_by_id(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        otp_data = OtpService.create_otp(user_id)
        if 'error' in otp_data:
            return jsonify({'error': 'Failed to generate OTP'}), 500

        email_result = EmailService.send_otp_email(
            to_email  = user['email'],
            user_name = user['full_name'],
            otp_code  = otp_data['otp_code']
        )
        if email_result['status'] == 'failed':
            return jsonify({'error': 'Failed to send OTP email'}), 500

        masked_email = OtpService.mask_email(user['email'])
        print(f"✅ OTP resent to {user['email']} for user {user_id}")

        return jsonify({
            'status' : 'otp_sent',
            'message': f'New OTP sent to {masked_email}',
            'email'  : masked_email
        }), 200

    except Exception as e:
        print(f"❌ Resend OTP error: {e}")
        return jsonify({'error': 'Internal server error'}), 500


# ============================================
# GET /api/auth/verify
# ============================================
@auth_bp.route('/api/auth/verify', methods=['GET'])
@jwt_required()
def verify_token():
    try:
        user = AuthService.get_current_user()
        if user:
            return jsonify(user), 200
        return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        print(f"❌ Verify error: {e}")
        return jsonify({'error': 'Internal server error'}), 500


# ============================================
# POST /api/auth/logout
# ============================================
@auth_bp.route('/api/auth/logout', methods=['POST'])
@jwt_required()
def logout():
    try:
        user_id = get_jwt_identity()
        print(f"📤 User {user_id} logged out")
        return jsonify({'message': 'Logged out successfully'}), 200
    except Exception as e:
        print(f"❌ Logout error: {e}")
        return jsonify({'error': 'Internal server error'}), 500


# ============================================
# GET /api/auth/me
# ============================================
@auth_bp.route('/api/auth/me', methods=['GET'])
@jwt_required()
def get_current_user_info():
    try:
        user = AuthService.get_current_user()
        if user:
            return jsonify(user), 200
        return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        print(f"❌ Get user error: {e}")
        return jsonify({'error': 'Internal server error'}), 500


# ============================================
# POST /api/auth/refresh
# ============================================
@auth_bp.route('/api/auth/refresh', methods=['POST'])
@jwt_required()
def refresh_token():
    try:
        # Get current user identity and claims
        user_id = get_jwt_identity()
        claims = get_jwt()

        # Generate new access token with same claims
        new_access_token = create_access_token(
            identity=user_id,
            additional_claims={
                'role': claims.get('role'),
                'email': claims.get('email'),
                'name': claims.get('name')
            },
            expires_delta=timedelta(hours=8)  # Same expiration as login
        )

        print(f"🔄 Token refreshed for user {user_id}")
        return jsonify({
            'access_token': new_access_token,
            'message': 'Token refreshed successfully'
        }), 200

    except Exception as e:
        print(f"❌ Token refresh error: {e}")
        return jsonify({'error': 'Internal server error'}), 500
