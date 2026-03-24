"""
Reset user passwords
ScholarSense - AI-Powered Academic Intelligence System
"""
import bcrypt
from backend.database.models import User
from backend.database.db_config import get_db

def reset_user_password(email: str, new_password: str):
    """Reset a user's password"""
    db = next(get_db())
    try:
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            print(f"❌ User {email} not found!")
            return False
        
        # Hash new password
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(new_password.encode('utf-8'), salt).decode('utf-8')
        
        # Update password
        user.password_hash = password_hash
        db.commit()
        
        print(f"✅ Password reset for {email}")
        return True
    except Exception as e:
        db.rollback()
        print(f"❌ Error resetting password: {e}")
        return False
    finally:
        db.close()

def verify_password_works(email: str, password: str):
    """Verify password works"""
    db = next(get_db())
    try:
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            print(f"❌ User {email} not found!")
            return False
        
        # Verify password
        result = bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8'))
        
        if result:
            print(f"✅ Password verification works for {email}")
        else:
            print(f"❌ Password verification failed for {email}")
        
        return result
    except Exception as e:
        print(f"❌ Error verifying password: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("🔐 RESETTING USER PASSWORDS")
    print("=" * 60)
    
    # Reset admin password
    print("\n1. Resetting admin password...")
    reset_user_password('admin@scholarsense.com', 'admin123')
    verify_password_works('admin@scholarsense.com', 'admin123')
    
    # Reset teacher password
    print("\n2. Resetting teacher password...")
    reset_user_password('teacher@scholarsense.com', 'teacher123')
    verify_password_works('teacher@scholarsense.com', 'teacher123')
    
    print("\n" + "=" * 60)
    print("✅ PASSWORD RESET COMPLETE!")
    print("=" * 60)
