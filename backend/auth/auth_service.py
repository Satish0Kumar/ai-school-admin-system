"""
Authentication Service - JWT-based authentication
ScholarSense - AI-Powered Academic Intelligence System
"""
import bcrypt
from datetime import datetime, timedelta
from flask_jwt_extended import create_access_token, get_jwt_identity
from backend.database.models import User
from backend.database.db_config import get_db

class AuthService:
    """Handle user authentication and authorization"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verify a password against its hash"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except Exception as e:
            print(f"Password verification error: {e}")
            return False
    
    @staticmethod
    def login(email: str, password: str):
        """
        Authenticate user and return JWT token
        Returns: dict with token and user info, or None if auth fails
        """
        db = next(get_db())
        try:
            # Find user by email
            user = db.query(User).filter(User.email == email, User.is_active == True).first()
            
            if not user:
                return None
            
            # Verify password
            if not AuthService.verify_password(password, user.password_hash):
                return None
            
            # Update last login
            user.last_login = datetime.utcnow()
            db.commit()
            
            # Create JWT token
            access_token = create_access_token(
                identity=str(user.id),
                additional_claims={
                    'role': user.role,
                    'email': user.email,
                    'name': user.full_name
                },
                expires_delta=timedelta(hours=8)
            )
            
            return {
                'access_token': access_token,
                'user': user.to_dict()
            }
        except Exception as e:
            print(f"Login error: {e}")
            return None
        finally:
            db.close()
    
    @staticmethod
    def create_user(username: str, email: str, password: str, full_name: str, role: str):
        """
        Create a new user (admin only)
        Returns: user dict or error dict
        """
        db = next(get_db())
        try:
            # Check if user exists
            existing = db.query(User).filter(
                (User.email == email) | (User.username == username)
            ).first()
            
            if existing:
                return {'error': 'User with this email or username already exists'}
            
            # Validate role
            if role not in ['admin', 'teacher']:
                return {'error': 'Invalid role. Must be "admin" or "teacher"'}
            
            # Hash password
            hashed = AuthService.hash_password(password)
            
            # Create user
            user = User(
                username=username,
                email=email,
                password_hash=hashed,
                full_name=full_name,
                role=role,
                is_active=True
            )
            
            db.add(user)
            db.commit()
            db.refresh(user)
            
            return user.to_dict()
        except Exception as e:
            db.rollback()
            print(f"Create user error: {e}")
            return {'error': str(e)}
        finally:
            db.close()
    
    @staticmethod
    def get_current_user():
        """Get current authenticated user from JWT"""
        user_id = int(get_jwt_identity())
        db = next(get_db())
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                return user.to_dict()
            return None
        finally:
            db.close()
    
    @staticmethod
    def get_all_users():
        """Get all users (admin only)"""
        db = next(get_db())
        try:
            users = db.query(User).all()
            return [user.to_dict() for user in users]
        finally:
            db.close()
    
    @staticmethod
    def change_password(user_id: int, old_password: str, new_password: str):
        """Change user password"""
        db = next(get_db())
        try:
            user = db.query(User).filter(User.id == user_id).first()
            
            if not user:
                return {'error': 'User not found'}
            
            # Verify old password
            if not AuthService.verify_password(old_password, user.password_hash):
                return {'error': 'Incorrect current password'}
            
            # Hash and update new password
            user.password_hash = AuthService.hash_password(new_password)
            db.commit()
            
            return {'message': 'Password changed successfully'}
        except Exception as e:
            db.rollback()
            print(f"Change password error: {e}")
            return {'error': str(e)}
        finally:
            db.close()

# Helper function to create default users
def create_default_users():
    """Create default admin and teacher if they don't exist"""
    print("\n🔐 Creating default users...")
    
    # Create admin
    admin_result = AuthService.create_user(
        username='admin',
        email='admin@scholarsense.com',
        password='admin123',
        full_name='System Administrator',
        role='admin'
    )
    
    if 'error' in admin_result:
        print(f"   ℹ️  Admin: {admin_result['error']}")
    else:
        print(f"   ✅ Admin created: {admin_result['email']}")
    
    # Create teacher
    teacher_result = AuthService.create_user(
        username='teacher',
        email='teacher@scholarsense.com',
        password='teacher123',
        full_name='Demo Teacher',
        role='teacher'
    )
    
    if 'error' in teacher_result:
        print(f"   ℹ️  Teacher: {teacher_result['error']}")
    else:
        print(f"   ✅ Teacher created: {teacher_result['email']}")
    
    print("\n📋 Default Login Credentials:")
    print("   Admin:")
    print("   └─ Email: admin@scholarsense.com")
    print("   └─ Password: admin123")
    print("\n   Teacher:")
    print("   └─ Email: teacher@scholarsense.com")
    print("   └─ Password: teacher123")

# Main test
if __name__ == "__main__":
    print("=" * 60)
    print("🔍 TESTING AUTHENTICATION SERVICE")
    print("=" * 60)
    
    # Create default users
    create_default_users()
    
    # Test password verification without JWT
    print("\n🧪 Testing password verification...")
    from backend.database.models import User
    from backend.database.db_config import get_db
    
    db = next(get_db())
    admin_user = db.query(User).filter(User.email == 'admin@scholarsense.com').first()
    
    if admin_user:
        # Test correct password
        correct = AuthService.verify_password('admin123', admin_user.password_hash)
        print(f"   ✅ Correct password: {correct}")
        
        # Test wrong password
        wrong = AuthService.verify_password('wrongpassword', admin_user.password_hash)
        print(f"   ✅ Wrong password rejected: {not wrong}")
        
        if correct and not wrong:
            print("\n   ✅ Password hashing and verification working perfectly!")
        else:
            print("\n   ❌ Password verification failed!")
    else:
        print("   ❌ Admin user not found!")
    
    db.close()
    
    print("\n💡 Note: JWT token generation requires Flask app context.")
    print("   Tokens will be generated when API starts.")
    print("\n" + "=" * 60)
