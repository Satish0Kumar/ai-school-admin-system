"""
OTP Service - Two Factor Authentication
ScholarSense - AI-Powered Academic Intelligence System

Handles:
- OTP generation
- OTP verification
- OTP expiry management
- Brute force protection (max 3 attempts)
"""

import secrets
import hashlib
import string
from datetime import datetime, timedelta
from collections import defaultdict
from backend.database.db_config import SessionLocal
from backend.database.models import OtpToken, User


from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)



# ── Constants ──────────────────────────────────────────────────────────────────
OTP_EXPIRY_MINUTES = 5      # OTP valid for 5 minutes
MAX_OTP_ATTEMPTS   = 3      # Max wrong attempts before lockout
LOCKOUT_MINUTES    = 15     # Lockout duration after max attempts

# Rate limiting
MAX_OTP_REQUESTS   = 3      # Max OTP requests per hour per user
RATE_LIMIT_WINDOW  = 3600   # 1 hour in seconds

# In-memory rate limiting (use Redis in production)
otp_request_counts = defaultdict(list)


class OtpService:
    """Handle OTP generation, sending, and verification"""

    # ──────────────────────────────────────────────────────────────────────────
    @staticmethod
    def generate_otp() -> str:
        """
        Generate a secure 6-digit OTP.
        Returns: 6-digit string e.g. '847392'
        """
        return ''.join(secrets.choice(string.digits) for _ in range(6))

    # ──────────────────────────────────────────────────────────────────────────
    @staticmethod
    def hash_otp(otp: str) -> str:
        """
        Hash OTP for secure storage.
        Uses SHA-256 with salt for additional security.
        """
        salt = secrets.token_hex(8)  # 16-character salt
        hashed = hashlib.sha256(f"{salt}{otp}".encode()).hexdigest()
        return f"{salt}:{hashed}"  # Store salt with hash

    # ──────────────────────────────────────────────────────────────────────────
    @staticmethod
    def verify_otp_hash(stored_hash: str, entered_otp: str) -> bool:
        """
        Verify entered OTP against stored hash.
        """
        try:
            salt, hash_value = stored_hash.split(':', 1)
            expected_hash = hashlib.sha256(f"{salt}{entered_otp}".encode()).hexdigest()
            return secrets.compare_digest(hash_value, expected_hash)
        except (ValueError, TypeError):
            return False

    # ──────────────────────────────────────────────────────────────────────────
    @staticmethod
    def check_rate_limit(user_id: int) -> dict:
        """
        Check if user has exceeded OTP request rate limit.
        Returns: {'allowed': bool, 'remaining_time': int} or {'error': str}
        """
        now = datetime.utcnow().timestamp()
        user_requests = otp_request_counts[user_id]

        # Remove old requests outside the window
        user_requests[:] = [req_time for req_time in user_requests
                           if now - req_time < RATE_LIMIT_WINDOW]

        if len(user_requests) >= MAX_OTP_REQUESTS:
            # Calculate remaining time until oldest request expires
            oldest_request = min(user_requests)
            remaining_time = int(RATE_LIMIT_WINDOW - (now - oldest_request))
            return {
                'allowed': False,
                'remaining_time': remaining_time,
                'message': f'Too many OTP requests. Try again in {remaining_time} seconds.'
            }

        return {'allowed': True}

    # ──────────────────────────────────────────────────────────────────────────
    @staticmethod
    def record_otp_request(user_id: int):
        """Record an OTP request for rate limiting."""
        now = datetime.utcnow().timestamp()
        otp_request_counts[user_id].append(now)

    # ──────────────────────────────────────────────────────────────────────────
    @staticmethod
    def create_otp(user_id: int) -> dict:
        """
        Generate OTP, save to DB, return OTP details.

        Args:
            user_id: ID of the user requesting OTP

        Returns:
            dict with otp_code, expires_at, user details
        """
        db = SessionLocal()
        try:
            # ── Check rate limit ─────────────────────────────────────────────
            rate_limit = OtpService.check_rate_limit(user_id)
            if not rate_limit.get('allowed', False):
                return {
                    'error': rate_limit.get('message', 'Rate limit exceeded')
                }

            # ── Check for lockout ───────────────────────────────────────────
            lockout_check = OtpService._check_lockout(db, user_id)
            if lockout_check:
                return {
                    'error': lockout_check['message']
                }

            # ── Invalidate any existing unused OTPs for this user ───────────
            existing_otps = db.query(OtpToken).filter(
                OtpToken.user_id == user_id,
                OtpToken.is_used == False
            ).all()

            for old_otp in existing_otps:
                old_otp.is_used = True

            # ── Generate new OTP ────────────────────────────────────────────
            otp_code   = OtpService.generate_otp()
            otp_hash   = OtpService.hash_otp(otp_code)
            expires_at = datetime.utcnow() + timedelta(minutes=OTP_EXPIRY_MINUTES)

            # ── Save to database ────────────────────────────────────────────
            otp_token = OtpToken(
                user_id    = user_id,
                otp_code   = otp_hash,  # Store hashed OTP
                expires_at = expires_at,
                is_used    = False,
                attempts   = 0
            )
            db.add(otp_token)
            db.commit()
            db.refresh(otp_token)

            # ── Record the request for rate limiting ───────────────────────
            OtpService.record_otp_request(user_id)

            # ── Get user details for email ──────────────────────────────────
            user = db.query(User).filter(User.id == user_id).first()

            print(f"✅ OTP created for user {user_id}: "
                  f"expires at {expires_at.strftime('%H:%M:%S')}")

            return {
                'otp_id'    : otp_token.id,
                'otp_code'  : otp_code,
                'expires_at': expires_at.isoformat(),
                'user_email': user.email if user else None,
                'user_name' : user.full_name if user else None,
                'user_id'   : user_id
            }

        except Exception as e:
            db.rollback()
            print(f"❌ OTP creation error: {e}")
            return {'error': str(e)}
        finally:
            db.close()

    # ──────────────────────────────────────────────────────────────────────────
    @staticmethod
    def verify_otp(user_id: int, entered_otp: str) -> dict:
        """
        Verify OTP entered by user.

        Args:
            user_id    : ID of the user
            entered_otp: OTP entered by user

        Returns:
            dict with status: 'valid' | 'invalid' | 'expired' | 'locked'
        """
        db = SessionLocal()
        try:
            now = datetime.utcnow()

            # ── Check for lockout ───────────────────────────────────────────
            lockout_check = OtpService._check_lockout(db, user_id)
            if lockout_check:
                return lockout_check

            # ── Get latest unused OTP for user ──────────────────────────────
            otp_token = db.query(OtpToken).filter(
                OtpToken.user_id == user_id,
                OtpToken.is_used == False
            ).order_by(OtpToken.created_at.desc()).first()

            if not otp_token:
                return {
                    'status' : 'invalid',
                    'message': 'No active OTP found. Please request a new OTP.'
                }

            # ── Check expiry ────────────────────────────────────────────────
            if now > otp_token.expires_at:
                otp_token.is_used = True
                db.commit()
                return {
                    'status' : 'expired',
                    'message': 'OTP has expired. Please request a new OTP.'
                }

            # ── Check OTP code ──────────────────────────────────────────────
            if not OtpService.verify_otp_hash(otp_token.otp_code, entered_otp.strip()):
                # Increment attempt counter
                otp_token.attempts += 1
                db.commit()

                remaining = MAX_OTP_ATTEMPTS - otp_token.attempts

                if otp_token.attempts >= MAX_OTP_ATTEMPTS:
                    # Lock the OTP
                    otp_token.is_used = True
                    db.commit()
                    print(f"🔒 User {user_id} locked out after "
                          f"{MAX_OTP_ATTEMPTS} failed attempts")
                    return {
                        'status' : 'locked',
                        'message': (f'Too many wrong attempts. '
                                    f'Account locked for {LOCKOUT_MINUTES} minutes.')
                    }

                print(f"❌ Wrong OTP for user {user_id}. "
                      f"{remaining} attempts remaining.")
                return {
                    'status'   : 'invalid',
                    'message'  : f'Wrong OTP. {remaining} attempts remaining.',
                    'remaining': remaining
                }

            # ── OTP is VALID ────────────────────────────────────────────────
            otp_token.is_used = True
            db.commit()

            print(f"✅ OTP verified successfully for user {user_id}")
            return {
                'status' : 'valid',
                'message': 'OTP verified successfully'
            }

        except Exception as e:
            db.rollback()
            print(f"❌ OTP verification error: {e}")
            return {'status': 'error', 'message': str(e)}
        finally:
            db.close()

    # ──────────────────────────────────────────────────────────────────────────
    @staticmethod
    def _check_lockout(db, user_id: int):
        """
        Check if user is currently locked out due to failed attempts.
        Returns lockout dict if locked, None if not locked.
        """
        lockout_cutoff = datetime.utcnow() - timedelta(minutes=LOCKOUT_MINUTES)

        # Count failed OTPs in lockout window
        failed_otps = db.query(OtpToken).filter(
            OtpToken.user_id  == user_id,
            OtpToken.is_used  == True,
            OtpToken.attempts >= MAX_OTP_ATTEMPTS,
            OtpToken.created_at >= lockout_cutoff
        ).count()

        if failed_otps > 0:
            # Find when lockout ends
            latest_locked = db.query(OtpToken).filter(
                OtpToken.user_id  == user_id,
                OtpToken.is_used  == True,
                OtpToken.attempts >= MAX_OTP_ATTEMPTS,
                OtpToken.created_at >= lockout_cutoff
            ).order_by(OtpToken.created_at.desc()).first()

            if latest_locked:
                unlock_at = (latest_locked.created_at
                             + timedelta(minutes=LOCKOUT_MINUTES))
                remaining_mins = int(
                    (unlock_at - datetime.utcnow()).total_seconds() / 60
                )
                return {
                    'status' : 'locked',
                    'message': (f'Account locked due to too many failed attempts. '
                                f'Try again in {remaining_mins} minutes.')
                }
        return None

    # ──────────────────────────────────────────────────────────────────────────
    @staticmethod
    def cleanup_expired_otps():
        """
        Delete all expired OTPs from database.
        Call this periodically to keep the table clean.
        """
        db = SessionLocal()
        try:
            expired = db.query(OtpToken).filter(
                OtpToken.expires_at < datetime.utcnow()
            ).all()

            count = len(expired)
            for otp in expired:
                db.delete(otp)

            db.commit()
            print(f"🧹 Cleaned up {count} expired OTPs")
            return count

        except Exception as e:
            db.rollback()
            print(f"❌ Cleanup error: {e}")
            return 0
        finally:
            db.close()

    # ──────────────────────────────────────────────────────────────────────────
    @staticmethod
    def mask_email(email: str) -> str:
        """
        Mask email for display on OTP screen.
        e.g. teacher@school.com → tea***@school.com
        """
        try:
            local, domain = email.split('@')
            if len(local) <= 3:
                masked_local = local[0] + '***'
            else:
                masked_local = local[:3] + '***'
            return f"{masked_local}@{domain}"
        except Exception:
            return '***@***.com'
