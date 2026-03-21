
"""
Flask REST API with JWT Authentication
ScholarSense - AI-Powered Academic Intelligence System
"""
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


from backend.services.attendance_service import AttendanceService

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, get_jwt
from dotenv import load_dotenv


from backend.services.student_service import StudentService
from backend.services.academic_service import AcademicService
from backend.services.prediction_service import PredictionService  # ← ADD THIS


from datetime import datetime, date, timedelta

# Load environment variables
load_dotenv()

# Import services
from backend.auth.auth_service import AuthService
from backend.database.db_config import test_connection, get_database_info

# ... rest of the code stays the same


# OTP imports - Enhancement 2
from backend.services.otp_service import OtpService
from backend.services.email_service import EmailService


# Notification imports - Enhancement 3
from backend.services.notification_service import NotificationService


# PDF imports - Enhancement 4
from backend.services.pdf_service import PDFService
from flask import send_file


from backend.services.student_service import StudentService
from backend.services.academic_service import AcademicService  # ← ADD THIS







"""
Flask REST API with JWT Authentication
ScholarSense - AI-Powered Academic Intelligence System
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, get_jwt
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Import services
from backend.auth.auth_service import AuthService
from backend.database.db_config import test_connection, get_database_info


from backend.auth.auth_service import AuthService
from backend.database.db_config import test_connection, get_database_info
from backend.services.student_service import StudentService  # ← ADD THIS



# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 28800))  # 8 hours


# JWT Additional Config
app.config['JWT_ALGORITHM'] = 'HS256'
app.config['PROPAGATE_EXCEPTIONS'] = True

# Debug: Print JWT config
print(f"\n🔐 JWT Configuration:")
print(f"   Secret Key Length: {len(app.config['JWT_SECRET_KEY'])} chars")
print(f"   Token Expiry: {app.config['JWT_ACCESS_TOKEN_EXPIRES']} seconds")
print(f"   Algorithm: {app.config['JWT_ALGORITHM']}\n")


# Enable CORS
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Initialize JWT
jwt = JWTManager(app)

# ============================================
# STARTUP & HEALTH CHECK
# ============================================

@app.before_request
def log_request():
    """Log all incoming requests (for debugging)"""
    if request.method != 'OPTIONS':
        print(f"📨 {request.method} {request.path}")

@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    Returns: System status and database info
    """
    db_info = get_database_info()
    
    return jsonify({
        'status': 'healthy',
        'service': 'ScholarSense API',
        'version': '2.0',
        'project': os.getenv('PROJECT_NAME', 'ScholarSense'),
        'database': db_info
    }), 200

# ============================================
# AUTHENTICATION ROUTES
# ============================================

@app.route('/api/auth/login', methods=['POST'])
def login():
    """
    MODIFIED: Step 1 of 2FA login
    Body: {"email": "user@email.com", "password": "password123"}
    
    Old behavior: validates credentials → returns JWT
    New behavior: validates credentials → sends OTP → returns otp_sent status
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        email    = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400

        # ── Step 1: Validate credentials (same as before) ──────────────────
        result = AuthService.login(email, password)

        if not result:
            print(f"❌ Login failed: {email}")
            return jsonify({'error': 'Invalid credentials'}), 401

        # ── Step 2: Credentials valid → Generate OTP ───────────────────────
        user    = result['user']
        user_id = user['id']

        otp_data = OtpService.create_otp(user_id)

        if 'error' in otp_data:
            print(f"❌ OTP generation failed: {otp_data['error']}")
            return jsonify({'error': 'Failed to generate OTP'}), 500

        # ── Step 3: Send OTP email ──────────────────────────────────────────
        email_result = EmailService.send_otp_email(
            to_email  = user['email'],
            user_name = user['full_name'],
            otp_code  = otp_data['otp_code']
        )

        if email_result['status'] == 'failed':
            print(f"❌ OTP email failed: {email_result['message']}")
            return jsonify({
                'error': 'Failed to send OTP email. '
                         'Please check email configuration.'
            }), 500

        # ── Step 4: Return OTP sent status (NOT the JWT token yet) ─────────
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
# OTP VERIFICATION ROUTES - Enhancement 2
# ============================================

@app.route('/api/auth/verify-otp', methods=['POST'])
def verify_otp():
    """
    Step 2 of 2FA login - Verify OTP and return JWT token
    Body: {"user_id": 1, "otp": "847392"}
    Returns: JWT token + user info (same as old login response)
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        user_id      = data.get('user_id')
        entered_otp  = data.get('otp', '').strip()

        if not user_id or not entered_otp:
            return jsonify({'error': 'user_id and otp are required'}), 400

        if len(entered_otp) != 6 or not entered_otp.isdigit():
            return jsonify({'error': 'OTP must be exactly 6 digits'}), 400

        # ── Verify OTP ──────────────────────────────────────────────────────
        verify_result = OtpService.verify_otp(user_id, entered_otp)

        if verify_result['status'] == 'locked':
            print(f"🔒 User {user_id} is locked out")
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

        # ── OTP Valid → Generate JWT token ──────────────────────────────────
        token_result = AuthService.generate_token_for_user(user_id)

        if not token_result:
            return jsonify({'error': 'Failed to generate token'}), 500

        print(f"✅ 2FA login complete for user {user_id}")
        return jsonify(token_result), 200

    except Exception as e:
        print(f"❌ OTP verify error: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/auth/resend-otp', methods=['POST'])
def resend_otp():
    """
    Resend OTP to user's email
    Body: {"user_id": 1}
    Returns: success message
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        user_id = data.get('user_id')

        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400

        # ── Get user details ────────────────────────────────────────────────
        user = AuthService.get_user_by_id(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        # ── Generate new OTP ────────────────────────────────────────────────
        otp_data = OtpService.create_otp(user_id)

        if 'error' in otp_data:
            return jsonify({'error': 'Failed to generate OTP'}), 500

        # ── Send OTP email ──────────────────────────────────────────────────
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




@app.route('/api/auth/verify', methods=['GET'])
@jwt_required()
def verify_token():
    """
    Verify JWT token and return current user
    Headers: Authorization: Bearer <token>
    Returns: Current user info
    """
    try:
        user = AuthService.get_current_user()
        if user:
            return jsonify(user), 200
        return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        print(f"❌ Verify error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/auth/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    Logout endpoint (client should delete token)
    Headers: Authorization: Bearer <token>
    """
    try:
        user_id = get_jwt_identity()
        print(f"📤 User {user_id} logged out")
        return jsonify({'message': 'Logged out successfully'}), 200
    except Exception as e:
        print(f"❌ Logout error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/auth/me', methods=['GET'])
@jwt_required()
def get_current_user_info():
    """
    Get current authenticated user info
    Headers: Authorization: Bearer <token>
    Returns: User information
    """
    try:
        user = AuthService.get_current_user()
        if user:
            return jsonify(user), 200
        return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        print(f"❌ Get user error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# ============================================
# USER MANAGEMENT ROUTES (Admin only)
# ============================================

@app.route('/api/users', methods=['GET'])
@jwt_required()
def get_all_users():
    """
    Get all users (admin only)
    Headers: Authorization: Bearer <token>
    Returns: List of all users
    """
    try:
        # Check if admin
        claims = get_jwt()
        if claims.get('role') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        users = AuthService.get_all_users()
        return jsonify(users), 200
    except Exception as e:
        print(f"❌ Get users error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/users/create', methods=['POST'])
@jwt_required()
def create_user():
    """
    Create new user (admin only)
    Headers: Authorization: Bearer <token>
    Body: {"username": "...", "email": "...", "password": "...", "full_name": "...", "role": "teacher"}
    Returns: Created user info
    """
    try:
        # Check if admin
        claims = get_jwt()
        if claims.get('role') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        data = request.get_json()
        required = ['username', 'email', 'password', 'full_name', 'role']
        
        if not all(key in data for key in required):
            return jsonify({'error': 'Missing required fields'}), 400
        
        result = AuthService.create_user(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            full_name=data['full_name'],
            role=data['role']
        )
        
        if 'error' in result:
            return jsonify(result), 400
        
        print(f"✅ User created: {result['email']}")
        return jsonify(result), 201
    
    except Exception as e:
        print(f"❌ Create user error: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({'message': 'Admin access required'}), 403
    try:
        from backend.database.dbconfig import SessionLocal
        from backend.database.models import User
        db = SessionLocal()
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            db.close()
            return jsonify({'message': 'User not found'}), 404
        db.delete(user)
        db.commit()
        db.close()
        print(f"🗑️ User deleted: ID {user_id}")
        return jsonify({'message': 'User deleted successfully'}), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/api/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user_status(user_id):
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({'message': 'Admin access required'}), 403
    data = request.get_json()
    try:
        from backend.database.dbconfig import SessionLocal
        from backend.database.models import User
        db = SessionLocal()
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            db.close()
            return jsonify({'message': 'User not found'}), 404
        user.is_active = data.get('is_active', True)
        db.commit()
        db.close()
        print(f"✅ User {user_id} status updated to {user.is_active}")
        return jsonify({'message': 'User updated successfully'}), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500





# ============================================
# STUDENT MANAGEMENT ROUTES
# ============================================

@app.route('/api/students', methods=['GET'])
@jwt_required()
def get_students():
    """
    Get all students with optional filters
    Query params: ?grade=10&section=A&search=name
    Returns: List of students
    """
    try:
        # Get query parameters
        grade = request.args.get('grade', type=int)
        section = request.args.get('section')
        search = request.args.get('search')
        
        if search:
            # Search students
            students = StudentService.search_students(search)
        else:
            # Get all students with filters
            students = StudentService.get_all_students(grade=grade, section=section)
        
        return jsonify(students), 200
    except Exception as e:
        print(f"❌ Get students error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/students/count', methods=['GET'])
@jwt_required()
def get_students_count():
    """
    Get total student count
    Query params: ?grade=10
    Returns: Count of students
    """
    try:
        grade = request.args.get('grade', type=int)
        result = StudentService.get_students_count(grade=grade)
        return jsonify(result), 200
    except Exception as e:
        print(f"❌ Get students count error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/students/<int:student_id>', methods=['GET'])
@jwt_required()
def get_student(student_id):
    """
    Get specific student by ID
    Returns: Student info
    """
    try:
        student = StudentService.get_student(student_id)
        
        if 'error' in student:
            return jsonify(student), 404
        
        return jsonify(student), 200
    except Exception as e:
        print(f"❌ Get student error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/students/<int:student_id>/details', methods=['GET'])
@jwt_required()
def get_student_details(student_id):
    """
    Get student with all related records (academic, attendance, predictions)
    Returns: Student info with all records
    """
    try:
        student = StudentService.get_student_with_records(student_id)
        
        if 'error' in student:
            return jsonify(student), 404
        
        return jsonify(student), 200
    except Exception as e:
        print(f"❌ Get student details error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/students', methods=['POST'])
@jwt_required()
def create_student():
    """
    Create new student
    Body: Student data (see StudentService for required fields)
    Returns: Created student info
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Required fields
        required = ['student_id', 'first_name', 'last_name', 'grade']
        if not all(field in data for field in required):
            return jsonify({'error': 'Missing required fields: student_id, first_name, last_name, grade'}), 400
        
        result = StudentService.create_student(data)
        
        if 'error' in result:
            return jsonify(result), 400
        
        print(f"✅ Student created: {result['student_id']} - {result['first_name']} {result['last_name']}")
        return jsonify(result), 201
    except Exception as e:
        print(f"❌ Create student error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/students/<int:student_id>', methods=['PUT'])
@jwt_required()
def update_student(student_id):
    """
    Update student information
    Body: Fields to update
    Returns: Updated student info
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        result = StudentService.update_student(student_id, data)
        
        if 'error' in result:
            return jsonify(result), 404
        
        print(f"✅ Student updated: ID {student_id}")
        return jsonify(result), 200
    except Exception as e:
        print(f"❌ Update student error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/students/<int:student_id>', methods=['DELETE'])
@jwt_required()
def delete_student(student_id):
    """
    Delete or deactivate student
    Query param: ?permanent=true for hard delete
    Returns: Success message
    """
    try:
        # Check if admin (only admins can delete)
        claims = get_jwt()
        if claims.get('role') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        permanent = request.args.get('permanent', 'false').lower() == 'true'
        soft_delete = not permanent
        
        result = StudentService.delete_student(student_id, soft_delete=soft_delete)
        
        if 'error' in result:
            return jsonify(result), 404
        
        print(f"✅ Student {'deactivated' if soft_delete else 'deleted'}: ID {student_id}")
        return jsonify(result), 200
    except Exception as e:
        print(f"❌ Delete student error: {e}")
        return jsonify({'error': 'Internal server error'}), 500




# ============================================
# ACADEMIC RECORDS ROUTES
# ============================================

@app.route('/api/students/<int:student_id>/academics', methods=['GET'])
@jwt_required()
def get_student_academics(student_id):
    """
    Get all academic records for a student
    Returns: List of academic records
    """
    try:
        records = AcademicService.get_student_academic_records(student_id)
        return jsonify(records), 200
    except Exception as e:
        print(f"❌ Get academics error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/students/<int:student_id>/academics/latest', methods=['GET'])
@jwt_required()
def get_student_latest_academic(student_id):
    """
    Get latest academic record for a student
    Returns: Latest academic record
    """
    try:
        record = AcademicService.get_latest_academic_record(student_id)
        
        if 'error' in record:
            return jsonify(record), 404
        
        return jsonify(record), 200
    except Exception as e:
        print(f"❌ Get latest academic error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/academics', methods=['POST'])
@jwt_required()
def create_academic_record():
    """
    Create academic record
    Body: Academic data (student_id, semester, scores, etc.)
    Returns: Created academic record
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Required fields
        required = ['student_id', 'semester', 'current_gpa']
        if not all(field in data for field in required):
            return jsonify({'error': 'Missing required fields: student_id, semester, current_gpa'}), 400
        
        result = AcademicService.create_academic_record(data)
        
        if 'error' in result:
            return jsonify(result), 400
        
        print(f"✅ Academic record created: Student {result['student_id']} - {result['semester']}")

        # ── Auto-trigger parent notification ───────────────────────────────
        try:
            notif_results = NotificationService.check_and_notify_academic(
                student_id         = result['student_id'],
                academic_record_id = result.get('id')
            )
            print(f"📨 Notification check: {notif_results}")
        except Exception as notif_err:
            print(f"⚠️  Notification error (non-critical): {notif_err}")

        return jsonify(result), 201

    except Exception as e:
        print(f"❌ Create academic record error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/academics/<int:record_id>', methods=['GET'])
@jwt_required()
def get_academic_record(record_id):
    """
    Get specific academic record by ID
    Returns: Academic record
    """
    try:
        record = AcademicService.get_academic_record(record_id)
        
        if 'error' in record:
            return jsonify(record), 404
        
        return jsonify(record), 200
    except Exception as e:
        print(f"❌ Get academic record error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/academics/<int:record_id>', methods=['PUT'])
@jwt_required()
def update_academic_record(record_id):
    """
    Update academic record
    Body: Fields to update
    Returns: Updated academic record
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        result = AcademicService.update_academic_record(record_id, data)
        
        if 'error' in result:
            return jsonify(result), 404
        
        print(f"✅ Academic record updated: ID {record_id}")
        return jsonify(result), 200
    except Exception as e:
        print(f"❌ Update academic record error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/academics/<int:record_id>', methods=['DELETE'])
@jwt_required()
def delete_academic_record(record_id):
    """
    Delete academic record (Admin only)
    Returns: Success message
    """
    try:
        # Check if admin
        claims = get_jwt()
        if claims.get('role') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        result = AcademicService.delete_academic_record(record_id)
        
        if 'error' in result:
            return jsonify(result), 404
        
        print(f"✅ Academic record deleted: ID {record_id}")
        return jsonify(result), 200
    except Exception as e:
        print(f"❌ Delete academic record error: {e}")
        return jsonify({'error': 'Internal server error'}), 500




# ============================================
# RISK PREDICTION ROUTES
# ============================================

@app.route('/api/students/<int:student_id>/predict', methods=['POST'])
@jwt_required()
def predict_student_risk(student_id):
    """
    Make risk prediction for a student
    Returns: Prediction result with probabilities
    """
    try:
        user_id = int(get_jwt_identity())
        
        result = PredictionService.make_prediction(student_id, predicted_by=user_id)
        
        if 'error' in result:
            return jsonify(result), 400
        
        print(f"✅ Prediction made for student {student_id}: {result['risk_label']} ({result['confidence_score']:.1f}%)")

        # ── Auto-trigger high risk notification ─────────────────────────────
        try:
            notif_result = NotificationService.check_and_notify_risk(
                student_id    = student_id,
                prediction_id = result.get('id'),
                risk_label    = result.get('risk_label', 'Low')
            )
            print(f"📨 Risk notification: {notif_result}")
        except Exception as notif_err:
            print(f"⚠️  Risk notification error (non-critical): {notif_err}")

        return jsonify(result), 201

    except Exception as e:
        print(f"❌ Prediction error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/students/<int:student_id>/predictions', methods=['GET'])
@jwt_required()
def get_student_prediction_history(student_id):
    """
    Get prediction history for a student
    Query param: ?limit=10
    Returns: List of predictions
    """
    try:
        limit = request.args.get('limit', 10, type=int)
        predictions = PredictionService.get_student_predictions(student_id, limit=limit)
        return jsonify(predictions), 200
    except Exception as e:
        print(f"❌ Get predictions error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/students/<int:student_id>/predictions/latest', methods=['GET'])
@jwt_required()
def get_student_latest_prediction(student_id):
    """
    Get latest prediction for a student
    Returns: Latest prediction
    """
    try:
        prediction = PredictionService.get_latest_prediction(student_id)
        
        if 'error' in prediction:
            return jsonify(prediction), 404
        
        return jsonify(prediction), 200
    except Exception as e:
        print(f"❌ Get latest prediction error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/predictions/high-risk', methods=['GET'])
@jwt_required()
def get_high_risk_students():
    """
    Get list of high-risk students
    Query param: ?grade=10
    Returns: List of students with high/critical risk
    """
    try:
        grade = request.args.get('grade', type=int)
        students = PredictionService.get_high_risk_students(grade=grade)
        return jsonify(students), 200
    except Exception as e:
        print(f"❌ Get high-risk students error: {e}")
        return jsonify({'error': 'Internal server error'}), 500







# ============================================
# JWT ERROR HANDLERS (with debug info)
# ============================================

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    print(f"❌ JWT Error: Token expired")
    print(f"   Header: {jwt_header}")
    print(f"   Payload: {jwt_payload}")
    return jsonify({'error': 'Token has expired'}), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    print(f"❌ JWT Error: Invalid token - {error}")
    return jsonify({'error': 'Invalid token', 'details': str(error)}), 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    print(f"❌ JWT Error: Missing token - {error}")
    return jsonify({'error': 'Authorization token required'}), 401

@jwt.token_verification_failed_loader
def token_verification_failed_callback(jwt_header, jwt_payload):
    print(f"❌ JWT Error: Token verification failed")
    print(f"   Header: {jwt_header}")
    print(f"   Payload: {jwt_payload}")
    return jsonify({'error': 'Token verification failed'}), 401

# ============================================
# STARTUP MESSAGE
# ============================================

def print_startup_message():
    """Print startup information"""
    print("\n" + "=" * 70)
    print("🎓 SCHOLARSENSE - AI-POWERED ACADEMIC INTELLIGENCE SYSTEM")
    print("=" * 70)
    print(f"📡 API Server: http://localhost:5000")
    print(f"🔐 Authentication: JWT (1 hour tokens)")
    print(f"💾 Database: PostgreSQL")
    print(f"🌐 CORS: Enabled")
    print(f"🤖 ML Model: {'Loaded' if PredictionService.model else 'Using dummy predictions'}")
    print("\n📚 Available Endpoints:")
    print("   Authentication:")
    print("   └─ POST /api/auth/login           - User login")
    print("   └─ GET  /api/auth/verify          - Verify token")
    print("   └─ GET  /api/auth/me              - Get current user")
    print("\n   User Management (Admin):")
    print("   └─ GET  /api/users                - Get all users")
    print("   └─ POST /api/users/create         - Create user")
    print("\n   Student Management:")
    print("   └─ GET    /api/students           - Get all students")
    print("   └─ GET    /api/students/{id}      - Get student")
    print("   └─ POST   /api/students           - Create student")
    print("   └─ PUT    /api/students/{id}      - Update student")
    print("   └─ DELETE /api/students/{id}      - Delete student")
    print("\n   Academic Records:")
    print("   └─ GET  /api/students/{id}/academics        - Get student academics")
    print("   └─ GET  /api/students/{id}/academics/latest - Get latest record")
    print("   └─ POST /api/academics                      - Create record")
    print("   └─ PUT  /api/academics/{id}                 - Update record")
    print("\n   Risk Predictions (ML):")
    print("   └─ POST /api/students/{id}/predict          - Make prediction")
    print("   └─ GET  /api/students/{id}/predictions      - Get history")
    print("   └─ GET  /api/students/{id}/predictions/latest - Latest prediction")
    print("   └─ GET  /api/predictions/high-risk          - High-risk students")
    print("\n   System:")
    print("   └─ GET  /api/health               - Health check")
    print("\n   Behavioral Incidents (Enhancement 4):")
    print("   └─ POST /api/incidents/log              - Log new incident")
    print("   └─ GET  /api/incidents                  - Get all incidents")
    print("   └─ GET  /api/students/{id}/incidents    - Student incidents")
    print("   └─ GET  /api/incidents/stats            - Incident stats")
    print("   └─ GET  /api/incidents/trends           - Incident trends")
    print("   └─ PUT  /api/incidents/{id}             - Update incident")
    print("   └─ DELETE /api/incidents/{id}           - Delete incident (Admin)")
    print("\n   Marks Entry (Enhancement 6):")
    print("   └─ POST /api/marks/entry              - Enter/update marks")
    print("   └─ GET  /api/marks/{grade}/{section}  - Get class marks")
    print("   └─ PUT  /api/marks/{record_id}        - Update marks record")
    print("   └─ GET  /api/marks/stats/{grade}      - Grade analytics")
    print("   └─ GET  /api/marks/failed             - Failed students")
    print("\n   Batch Risk Analysis (Enhancement 8):")
    print("   └─ POST /api/batch/run              - Run batch predictions")
    print("   └─ GET  /api/batch/predictions      - Get all stored predictions")
    print("   └─ GET  /api/batch/summary          - School-wide risk summary")
    print("   └─ GET  /api/batch/unpredicted      - Students with no prediction")
    print("\n   Parent Communications (Enhancement 9):")
    print("   └─ POST /api/communications/send          - Send email to parent")
    print("   └─ POST /api/communications/batch         - Batch send emails")
    print("   └─ GET  /api/communications/history       - Communication history")
    print("   └─ GET  /api/communications/stats         - Comm statistics")
    print("   └─ GET  /api/communications/templates     - Email templates")
    print("   └─ GET  /api/students/{id}/communications - Student comm history")
    print("\n   Advanced Analytics (Enhancement 10):")
    print("   └─ GET /api/analytics/school-overview  - School-wide KPIs")
    print("   └─ GET /api/analytics/trends           - Time-series trends")


    print("\n   PDF Reports (Enhancement 4):")
    print("   └─ GET /api/reports/student/{id}  - Student PDF report")
    print("   └─ GET /api/reports/grade/{grade} - Grade wise PDF report")
    print("   └─ GET /api/reports/atrisk        - At-risk students PDF")
    print("   └─ GET /api/reports/preview/student/{id} - Preview in browser")

    print("\n   Notifications (Enhancement 3):")
    print("   └─ GET  /api/notifications              - All notifications")
    print("   └─ GET  /api/notifications/stats        - Notification stats")
    print("   └─ GET  /api/students/{id}/notifications - Student notifications")
    print("   └─ POST /api/students/{id}/notify       - Manual notify parent")
    print("   └─ POST /api/students/{id}/notify/check - Auto-check & notify")
    print("   └─ POST /api/notifications/bulk-check   - Bulk check all students")

    print("\n🔑 Test Credentials:")
    print("   Admin:   admin@scholarsense.com / admin123")
    print("   Teacher: teacher@scholarsense.com / teacher123")
    print("=" * 70 + "\n")






# ============================================
# ATTENDANCE ENDPOINTS
# ============================================

@app.route('/api/attendance/mark', methods=['POST'])
@jwt_required()
def mark_attendance():
    """Mark attendance for a student"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required = ['student_id', 'date', 'status']
        if not all(field in data for field in required):
            return jsonify({'error': 'Missing required fields'}), 400
        
        current_user = get_jwt_identity()
        
        result = AttendanceService.mark_attendance(
            student_id=data['student_id'],
            attendance_date=datetime.strptime(data['date'], '%Y-%m-%d').date(),
            status=data['status'],
            remarks=data.get('remarks'),
            marked_by=current_user
        )
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/attendance/bulk', methods=['POST'])
@jwt_required()
def mark_bulk_attendance():
    """Mark attendance for multiple students"""
    try:
        data = request.get_json()
        attendance_list = data.get('attendance_list', [])
        
        if not attendance_list:
            return jsonify({'error': 'No attendance data provided'}), 400
        
        current_user = get_jwt_identity()
        
        result = AttendanceService.mark_bulk_attendance(
            attendance_list=attendance_list,
            marked_by=current_user
        )
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/students/<int:student_id>/attendance', methods=['GET'])
@jwt_required()
def get_student_attendance(student_id):
    """Get attendance records for a student"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        records = AttendanceService.get_student_attendance(
            student_id=student_id,
            start_date=start_date,
            end_date=end_date
        )
        
        return jsonify(records), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/students/<int:student_id>/attendance/stats', methods=['GET'])
@jwt_required()
def get_attendance_stats(student_id):
    """Get attendance statistics for a student"""
    try:
        days = int(request.args.get('days', 30))
        
        stats = AttendanceService.get_attendance_stats(
            student_id=student_id,
            days=days
        )
        
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500



@app.route('/api/attendance/daily', methods=['GET'])
@jwt_required()
def get_daily_attendance():
    """Get attendance for all students on a specific date"""
    try:
        date_str = request.args.get('date')
        grade_str = request.args.get('grade')
        section = request.args.get('section')
        
        if not date_str:
            return jsonify({'error': 'Date parameter required'}), 400
        
        attendance_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        # Convert grade to int or None
        grade = None
        if grade_str and grade_str != 'None':
            try:
                grade = int(grade_str)
            except:
                grade = None
        
        # Handle section
        if section == 'None' or not section:
            section = None
        
        print(f"🔍 API Endpoint: date={attendance_date}, grade={grade}, section={section}")  # Debug
        
        results = AttendanceService.get_daily_attendance(
            attendance_date=attendance_date,
            grade=grade,
            section=section
        )
        
        print(f"✅ API Endpoint: Returning {len(results)} students")  # Debug
        
        return jsonify(results), 200
    except Exception as e:
        print(f"❌ API Endpoint Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/attendance/low-attendance', methods=['GET'])
@jwt_required()
def get_low_attendance_students_endpoint():
    """Get students with low attendance"""
    try:
        threshold = float(request.args.get('threshold', 75.0))
        days = int(request.args.get('days', 30))
        
        results = AttendanceService.get_low_attendance_students(
            threshold=threshold,
            days=days
        )
        
        return jsonify(results), 200
    except Exception as e:
        print(f"❌ Low attendance endpoint error: {e}")
        return jsonify({'error': str(e)}), 500



# ================================================================
# NOTIFICATION ROUTES - Enhancement 3
# ================================================================

@app.route('/api/notifications', methods=['GET'])
@jwt_required()
def get_notifications():
    """Get recent notifications across all students"""
    try:
        limit         = request.args.get('limit', 50, type=int)
        notifications = NotificationService.get_recent_notifications(limit=limit)
        return jsonify(notifications), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/notifications/stats', methods=['GET'])
@jwt_required()
def get_notification_stats():
    """Get notification statistics for dashboard"""
    try:
        stats = NotificationService.get_notification_stats()
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/students/<int:student_id>/notifications', methods=['GET'])
@jwt_required()
def get_student_notifications(student_id):
    """Get notification history for a specific student"""
    try:
        limit         = request.args.get('limit', 20, type=int)
        notifications = NotificationService.get_student_notifications(
            student_id = student_id,
            limit      = limit
        )
        return jsonify(notifications), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/students/<int:student_id>/notify', methods=['POST'])
@jwt_required()
def send_manual_notification(student_id):
    """
    Manually send notification to student's parent.
    Body: {"notification_type": "low_gpa", "message": "Custom message"}
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        notification_type = data.get('notification_type', 'high_risk')
        message           = data.get('message', '')

        if not message:
            return jsonify({'error': 'Message is required'}), 400

        valid_types = ['low_gpa', 'high_risk', 'low_attendance', 'failed_subjects']
        if notification_type not in valid_types:
            return jsonify({
                'error': f'Invalid type. Must be one of: {valid_types}'
            }), 400

        result = NotificationService.send_manual_notification(
            student_id        = student_id,
            notification_type = notification_type,
            custom_message    = message
        )

        if result['status'] == 'sent':
            return jsonify(result), 200
        else:
            return jsonify({'error': result.get('message', 'Send failed')}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/students/<int:student_id>/notify/check', methods=['POST'])
@jwt_required()
def check_and_notify_student(student_id):
    """
    Manually trigger academic check for a specific student.
    Sends notifications if any conditions are met.
    """
    try:
        results = NotificationService.check_and_notify_academic(
            student_id = student_id
        )

        sent    = [r for r in results if r.get('status') == 'sent']
        failed  = [r for r in results if r.get('status') == 'failed']
        skipped = [r for r in results if r.get('status') in
                   ('no_trigger', 'skipped', 'cooldown')]

        return jsonify({
            'student_id'   : student_id,
            'total_checked': len(results),
            'sent'         : len(sent),
            'failed'       : len(failed),
            'skipped'      : len(skipped),
            'results'      : results
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/notifications/bulk-check', methods=['POST'])
@jwt_required()
def bulk_notification_check():
    """
    Run notification check for ALL active students.
    Body (optional): {"grade": 9, "section": "A"}
    """
    try:
        data    = request.get_json() or {}
        grade   = data.get('grade')
        section = data.get('section')

        from backend.database.db_config import SessionLocal
        from backend.database.models import Student as StudentModel

        db = SessionLocal()
        try:
            query = db.query(StudentModel).filter(
                StudentModel.is_active == True
            )
            if grade:
                query = query.filter(StudentModel.grade == grade)
            if section:
                query = query.filter(StudentModel.section == section)
            students = query.all()
            total    = len(students)
        finally:
            db.close()

        print(f"🔄 Bulk notification check: {total} students")

        summary = {
            'total_students': total,
            'sent'          : 0,
            'failed'        : 0,
            'no_trigger'    : 0,
            'skipped'       : 0
        }

        for student in students:
            results = NotificationService.check_and_notify_academic(
                student_id = student.id
            )
            for r in results:
                status = r.get('status', 'skipped')
                if   status == 'sent'      : summary['sent']       += 1
                elif status == 'failed'    : summary['failed']     += 1
                elif status == 'no_trigger': summary['no_trigger'] += 1
                else                       : summary['skipped']    += 1

        print(f"✅ Bulk check complete: {summary}")
        return jsonify(summary), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500




# ================================================================
# PDF REPORT ROUTES - Enhancement 4
# ================================================================

@app.route('/api/reports/student/<int:student_id>', methods=['GET'])
@jwt_required()
def download_student_report(student_id):
    """
    Download individual student PDF report.
    Returns: PDF file download
    """
    try:
        pdf_bytes = PDFService.generate_student_report(student_id)

        buffer = __import__('io').BytesIO(pdf_bytes)
        buffer.seek(0)

        filename = f"student_{student_id}_report_{datetime.now().strftime('%Y%m%d')}.pdf"

        return send_file(
            buffer,
            mimetype             = 'application/pdf',
            as_attachment        = True,
            download_name        = filename
        )

    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        print(f"❌ Student PDF error: {e}")
        return jsonify({'error': 'Failed to generate PDF'}), 500


@app.route('/api/reports/grade/<int:grade>', methods=['GET'])
@jwt_required()
def download_grade_report(grade):
    """
    Download grade/class wise PDF report.
    Query param: ?section=A (optional)
    Returns: PDF file download
    """
    try:
        section = request.args.get('section')
        if section in ('None', 'All', ''):
            section = None

        pdf_bytes = PDFService.generate_grade_report(grade, section)

        buffer = __import__('io').BytesIO(pdf_bytes)
        buffer.seek(0)

        sec_str  = f"_sec{section}" if section else ""
        filename = f"grade{grade}{sec_str}_report_{datetime.now().strftime('%Y%m%d')}.pdf"

        return send_file(
            buffer,
            mimetype      = 'application/pdf',
            as_attachment = True,
            download_name = filename
        )

    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        print(f"❌ Grade PDF error: {e}")
        return jsonify({'error': 'Failed to generate PDF'}), 500


@app.route('/api/reports/atrisk', methods=['GET'])
@jwt_required()
def download_atrisk_report():
    """
    Download at-risk students PDF report.
    Query param: ?grade=9 (optional)
    Returns: PDF file download
    """
    try:
        grade = request.args.get('grade', type=int)

        pdf_bytes = PDFService.generate_atrisk_report(grade=grade)

        buffer = __import__('io').BytesIO(pdf_bytes)
        buffer.seek(0)

        grade_str = f"_grade{grade}" if grade else "_all_grades"
        filename  = f"atrisk{grade_str}_report_{datetime.now().strftime('%Y%m%d')}.pdf"

        return send_file(
            buffer,
            mimetype      = 'application/pdf',
            as_attachment = True,
            download_name = filename
        )

    except Exception as e:
        print(f"❌ At-risk PDF error: {e}")
        return jsonify({'error': 'Failed to generate PDF'}), 500


@app.route('/api/reports/preview/student/<int:student_id>', methods=['GET'])
@jwt_required()
def preview_student_report(student_id):
    """
    Preview individual student PDF in browser (no download).
    Returns: PDF inline view
    """
    try:
        pdf_bytes = PDFService.generate_student_report(student_id)

        buffer = __import__('io').BytesIO(pdf_bytes)
        buffer.seek(0)

        return send_file(
            buffer,
            mimetype      = 'application/pdf',
            as_attachment = False
        )

    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        print(f"❌ Preview PDF error: {e}")
        return jsonify({'error': 'Failed to generate PDF'}), 500




# ================================================================
# BEHAVIORAL INCIDENT ROUTES - Enhancement 4
# ================================================================
from backend.services.behavioral_service import BehavioralService

@app.route('/api/incidents/log', methods=['POST'])
@jwt_required()
def log_incident():
    """
    Log a new behavioral incident
    Body: {
        "student_id": 1,
        "incident_date": "2026-03-18",
        "incident_time": "10:30:00",       ← optional
        "incident_type": "Disciplinary",
        "severity": "Minor",
        "description": "Student disrupted class",
        "location": "Classroom 5A",        ← optional
        "action_taken": "Verbal warning",  ← optional
        "witnesses": "Teacher Ramesh",     ← optional
        "parent_notified": false,          ← optional
        "counseling_given": false,         ← optional
        "follow_up_date": "2026-03-25",    ← optional
        "notes": "First offence"           ← optional
    }
    Returns: {"status": "success", "data": {...}}
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"status": "error", "message": "No data provided"}), 400

        # Get reporter from JWT
        reporter_id = int(get_jwt_identity())

        result = BehavioralService.log_incident(data, reporter_id)

        if result['status'] == 'error':
            return jsonify(result), 400

        print(f"✅ Incident logged by user {reporter_id}")
        return jsonify(result), 201

    except Exception as e:
        print(f"❌ Log incident endpoint error: {e}")
        return jsonify({"status": "error", "message": "Internal server error"}), 500


@app.route('/api/incidents', methods=['GET'])
@jwt_required()
def get_incidents():
    """
    Get all incidents with optional filters
    Query params:
        ?student_id=1
        &date_from=2026-01-01
        &date_to=2026-03-31
        &severity=Critical
        &type=Bullying
        &limit=50
        &offset=0
    Returns: {"status": "success", "data": {"incidents": [...], "total": int}}
    """
    try:
        filters = {}

        # Parse query params
        if request.args.get('student_id'):
            filters['student_id'] = int(request.args.get('student_id'))

        if request.args.get('date_from'):
            from datetime import date as dt_date
            filters['date_from'] = datetime.strptime(
                request.args.get('date_from'), '%Y-%m-%d'
            ).date()

        if request.args.get('date_to'):
            filters['date_to'] = datetime.strptime(
                request.args.get('date_to'), '%Y-%m-%d'
            ).date()

        if request.args.get('severity'):
            filters['severity'] = request.args.get('severity')

        if request.args.get('type'):
            filters['type'] = request.args.get('type')

        filters['limit']  = request.args.get('limit',  50,  type=int)
        filters['offset'] = request.args.get('offset', 0,   type=int)

        result = BehavioralService.get_incidents(filters)

        if result['status'] == 'error':
            return jsonify(result), 500

        return jsonify(result), 200

    except Exception as e:
        print(f"❌ Get incidents endpoint error: {e}")
        return jsonify({"status": "error", "message": "Internal server error"}), 500


@app.route('/api/students/<int:student_id>/incidents', methods=['GET'])
@jwt_required()
def get_student_incidents(student_id):
    """
    Get all incidents for a specific student
    Query param: ?limit=20
    Returns: {"status": "success", "data": {"incidents": [...], "total": int}}
    """
    try:
        limit  = request.args.get('limit', 20, type=int)
        result = BehavioralService.get_student_incidents(student_id, limit=limit)

        if result['status'] == 'error':
            return jsonify(result), 500

        return jsonify(result), 200

    except Exception as e:
        print(f"❌ Get student incidents endpoint error: {e}")
        return jsonify({"status": "error", "message": "Internal server error"}), 500


@app.route('/api/incidents/stats', methods=['GET'])
@jwt_required()
def get_incident_stats():
    """
    Get incident statistics for dashboard
    Query param: ?range=30_days   (7_days | 30_days | 90_days | all_time)
    Returns: {"status": "success", "data": {stats...}}
    """
    try:
        date_range = request.args.get('range', '30_days')
        result     = BehavioralService.get_incident_stats(date_range)

        if result['status'] == 'error':
            return jsonify(result), 500

        return jsonify(result), 200

    except Exception as e:
        print(f"❌ Incident stats endpoint error: {e}")
        return jsonify({"status": "error", "message": "Internal server error"}), 500


@app.route('/api/incidents/trends', methods=['GET'])
@jwt_required()
def get_incident_trends():
    """
    Get incident trend data (daily counts for line chart)
    Query param: ?days=30
    Returns: {"status": "success", "data": {"trends": [...], "period_days": int}}
    """
    try:
        days   = request.args.get('days', 30, type=int)
        result = BehavioralService.get_incident_trends(days)

        if result['status'] == 'error':
            return jsonify(result), 500

        return jsonify(result), 200

    except Exception as e:
        print(f"❌ Incident trends endpoint error: {e}")
        return jsonify({"status": "error", "message": "Internal server error"}), 500


@app.route('/api/incidents/<int:incident_id>', methods=['PUT'])
@jwt_required()
def update_incident(incident_id):
    """
    Update a behavioral incident
    Body: fields to update (severity, action_taken, parent_notified, etc.)
    Returns: {"status": "success", "data": {...}}
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"status": "error", "message": "No data provided"}), 400

        result = BehavioralService.update_incident(incident_id, data)

        if result['status'] == 'error':
            return jsonify(result), 404

        print(f"✅ Incident {incident_id} updated")
        return jsonify(result), 200

    except Exception as e:
        print(f"❌ Update incident endpoint error: {e}")
        return jsonify({"status": "error", "message": "Internal server error"}), 500


@app.route('/api/incidents/<int:incident_id>', methods=['DELETE'])
@jwt_required()
def delete_incident(incident_id):
    """
    Delete a behavioral incident (Admin only)
    Returns: {"status": "success", "message": "..."}
    """
    try:
        # Admin only
        claims = get_jwt()
        if claims.get('role') != 'admin':
            return jsonify({"status": "error", "message": "Admin access required"}), 403

        result = BehavioralService.delete_incident(incident_id)

        if result['status'] == 'error':
            return jsonify(result), 404

        print(f"✅ Incident {incident_id} deleted by admin")
        return jsonify(result), 200

    except Exception as e:
        print(f"❌ Delete incident endpoint error: {e}")
        return jsonify({"status": "error", "message": "Internal server error"}), 500




# ================================================================
# MARKS ENTRY ROUTES - Enhancement 6
# ================================================================
from backend.services.marks_service import MarksService

@app.route('/api/marks/entry', methods=['POST'])
@jwt_required()
def enter_marks():
    """
    Enter marks for a student
    Body: {
        "student_id": 1,
        "semester": "2025-2026 Sem 1",
        "exam_type": "Mid Term",
        "math_score": 78.5,
        "science_score": 82.0,
        "english_score": 75.0,
        "social_score": 88.0,
        "language_score": 91.0,
        "assignment_submission_rate": 95.0,  ← optional
        "remarks": "Good performance"         ← optional
    }
    Returns: {"status": "success", "data": {...}, "action": "created/updated"}
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"status": "error", "message": "No data provided"}), 400

        # Get teacher/admin from JWT
        entered_by = int(get_jwt_identity())

        result = MarksService.enter_marks(data, entered_by)

        if result['status'] == 'error':
            return jsonify(result), 400

        action      = result.get('action', 'created')
        status_code = 201 if action == 'created' else 200

        print(f"✅ Marks {action} by user {entered_by} "
              f"for student {data.get('student_id')}")

        return jsonify(result), status_code

    except Exception as e:
        print(f"❌ Enter marks endpoint error: {e}")
        return jsonify({"status": "error", "message": "Internal server error"}), 500


@app.route('/api/marks/<int:grade>/<string:section>', methods=['GET'])
@jwt_required()
def get_class_marks(grade, section):
    """
    Get all marks for a grade/section
    Path params: grade (6-10), section (A/B/C/All)
    Query params:
        ?semester=2025-2026 Sem 1
        &exam_type=Mid Term
    Returns: {"status": "success", "data": {"marks": [...], "total": int}}
    """
    try:
        semester  = request.args.get('semester')
        exam_type = request.args.get('exam_type')

        # Handle "All" section → pass None to service
        section_filter = None if section in ('All', 'all', 'None') else section

        result = MarksService.get_class_marks(
            grade     = grade,
            section   = section_filter,
            semester  = semester,
            exam_type = exam_type
        )

        if result['status'] == 'error':
            return jsonify(result), 500

        return jsonify(result), 200

    except Exception as e:
        print(f"❌ Get class marks endpoint error: {e}")
        return jsonify({"status": "error", "message": "Internal server error"}), 500


@app.route('/api/marks/<int:record_id>', methods=['PUT'])
@jwt_required()
def update_marks(record_id):
    """
    Update an existing marks record
    Body: {
        "math_score": 85.0,
        "science_score": 90.0,
        ...any score fields...
        "remarks": "Updated after recheck"
    }
    Returns: {"status": "success", "data": {...}}
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"status": "error", "message": "No data provided"}), 400

        result = MarksService.update_marks(record_id, data)

        if result['status'] == 'error':
            return jsonify(result), 404

        print(f"✅ Marks record {record_id} updated")
        return jsonify(result), 200

    except Exception as e:
        print(f"❌ Update marks endpoint error: {e}")
        return jsonify({"status": "error", "message": "Internal server error"}), 500


@app.route('/api/marks/stats/<int:grade>', methods=['GET'])
@jwt_required()
def get_marks_stats(grade):
    """
    Get marks analytics for a grade
    Query param: ?section=A  (optional)
    Returns: {
        "status": "success",
        "data": {
            "avg_gpa", "highest_gpa", "lowest_gpa",
            "total_failed", "subject_averages",
            "top_performers", "gpa_distribution"
        }
    }
    """
    try:
        section = request.args.get('section')
        if section in ('All', 'all', 'None', ''):
            section = None

        result = MarksService.get_marks_stats(grade, section)

        if result['status'] == 'error':
            return jsonify(result), 500

        return jsonify(result), 200

    except Exception as e:
        print(f"❌ Marks stats endpoint error: {e}")
        return jsonify({"status": "error", "message": "Internal server error"}), 500


@app.route('/api/marks/failed', methods=['GET'])
@jwt_required()
def get_failed_students():
    """
    Get students who failed one or more subjects
    Query params:
        ?grade=9
        &semester=2025-2026 Sem 1
    Returns: {"status": "success", "data": {"failed_students": [...], "total": int}}
    """
    try:
        grade    = request.args.get('grade',    type=int)
        semester = request.args.get('semester')

        result = MarksService.identify_failed_students(
            grade    = grade,
            semester = semester
        )

        if result['status'] == 'error':
            return jsonify(result), 500

        return jsonify(result), 200

    except Exception as e:
        print(f"❌ Failed students endpoint error: {e}")
        return jsonify({"status": "error", "message": "Internal server error"}), 500




# ================================================================
# BATCH RISK ANALYSIS ROUTES - Enhancement 8
# ================================================================
from backend.services.batch_service import BatchService

@app.route('/api/batch/run', methods=['POST'])
@jwt_required()
def run_batch_predictions():
    """
    Run ML predictions for all/filtered students
    Body (all optional): {
        "grade":   9,
        "section": "A"
    }
    Returns: {
        "status": "success",
        "data": {
            "summary": {
                "total": 120, "success": 115,
                "skipped": 3, "failed": 2,
                "risk_summary": {"Low":60,"Medium":30,"High":20,"Critical":5},
                "run_at": "...", "triggered_by": 1
            },
            "results": [{...per student...}]
        }
    }
    """
    try:
        data    = request.get_json() or {}
        filters = {}

        if data.get('grade'):
            filters['grade']   = int(data['grade'])
        if data.get('section') and data['section'] not in ('All', 'all'):
            filters['section'] = data['section']

        triggered_by = int(get_jwt_identity())

        print(f"🔁 Batch prediction triggered by user {triggered_by} "
              f"| filters: {filters}")

        result = BatchService.run_batch_predictions(
            filters      = filters,
            triggered_by = triggered_by
        )

        if result['status'] == 'error':
            return jsonify(result), 400

        return jsonify(result), 200

    except Exception as e:
        print(f"❌ Batch run endpoint error: {e}")
        return jsonify({"status": "error", "message": "Internal server error"}), 500


@app.route('/api/batch/predictions', methods=['GET'])
@jwt_required()
def get_all_predictions():
    """
    Get latest stored predictions for all students
    (Read-only — does NOT re-run ML)
    Query params:
        ?grade=9
        &section=A
        &risk_label=Critical
        &limit=200
    Returns: {
        "status": "success",
        "data": {
            "students":     [{...}],
            "total":        int,
            "risk_summary": {"Low":x,"Medium":x,"High":x,"Critical":x}
        }
    }
    """
    try:
        filters = {}

        if request.args.get('grade'):
            filters['grade']      = int(request.args.get('grade'))

        if request.args.get('section') and \
           request.args.get('section') not in ('All', 'all', ''):
            filters['section']    = request.args.get('section')

        if request.args.get('risk_label') and \
           request.args.get('risk_label') != 'All':
            filters['risk_label'] = request.args.get('risk_label')

        filters['limit'] = request.args.get('limit', 200, type=int)

        result = BatchService.get_all_predictions(filters)

        if result['status'] == 'error':
            return jsonify(result), 500

        return jsonify(result), 200

    except Exception as e:
        print(f"❌ Get all predictions endpoint error: {e}")
        return jsonify({"status": "error", "message": "Internal server error"}), 500


@app.route('/api/batch/summary', methods=['GET'])
@jwt_required()
def get_batch_summary():
    """
    Get school-wide risk summary stats
    Returns: {
        "status": "success",
        "data": {
            "risk_summary":      {"Low":x,...},
            "total_active":      int,
            "total_predicted":   int,
            "total_unpredicted": int,
            "avg_confidence":    float
        }
    }
    """
    try:
        result = BatchService.get_batch_summary()

        if result['status'] == 'error':
            return jsonify(result), 500

        return jsonify(result), 200

    except Exception as e:
        print(f"❌ Batch summary endpoint error: {e}")
        return jsonify({"status": "error", "message": "Internal server error"}), 500


@app.route('/api/batch/unpredicted', methods=['GET'])
@jwt_required()
def get_unpredicted_students():
    """
    Get students who have no risk prediction yet
    Query param: ?grade=9  (optional)
    Returns: {
        "status": "success",
        "data": {"students": [...], "total": int}
    }
    """
    try:
        grade  = request.args.get('grade', type=int)
        result = BatchService.get_unpredicted_students(grade=grade)

        if result['status'] == 'error':
            return jsonify(result), 500

        return jsonify(result), 200

    except Exception as e:
        print(f"❌ Unpredicted students endpoint error: {e}")
        return jsonify({"status": "error", "message": "Internal server error"}), 500



# ================================================================
# PARENT COMMUNICATION ROUTES - Enhancement 9
# ================================================================
from backend.services.communication_service import CommunicationService

@app.route('/api/communications/send', methods=['POST'])
@jwt_required()
def send_communication():
    """
    Send email to parent of a student
    Body: {
        "student_id": 1,
        "communication_type": "Risk Alert",
        "custom_subject": "...",       ← required only for Custom type
        "custom_message": "...",       ← required only for Custom type
        "extra_data": {                ← optional, enriches template
            "gpa": 45.5,
            "failed_subjects": 2,
            "risk_label": "High",
            "semester": "2025-2026 Sem 1",
            "total_marks": 227.5,
            "custom_message": "..."
        }
    }
    Returns: {"status": "success", "data": {...}}
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "status":  "error",
                "message": "No data provided"
            }), 400

        sent_by = int(get_jwt_identity())
        result  = CommunicationService.send_communication(data, sent_by)

        if result['status'] == 'error':
            return jsonify(result), 400

        print(f"✅ Communication sent by user {sent_by} "
              f"to student {data.get('student_id')}")
        return jsonify(result), 201

    except Exception as e:
        print(f"❌ Send communication endpoint error: {e}")
        return jsonify({
            "status":  "error",
            "message": "Internal server error"
        }), 500


@app.route('/api/communications/batch', methods=['POST'])
@jwt_required()
def batch_send_communications():
    """
    Send same communication type to multiple students at once
    Body: {
        "student_ids": [1, 2, 3, 4],
        "communication_type": "Risk Alert",
        "extra_data": {
            "risk_label": "High",
            "gpa": "N/A"
        }
    }
    Returns: {
        "status": "success",
        "data": {"sent": 3, "failed": 1, "total": 4, "results": [...]}
    }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "status":  "error",
                "message": "No data provided"
            }), 400

        student_ids = data.get('student_ids', [])
        if not student_ids:
            return jsonify({
                "status":  "error",
                "message": "student_ids list is required"
            }), 400

        comm_type  = data.get('communication_type', 'Custom')
        extra_data = data.get('extra_data', {})
        sent_by    = int(get_jwt_identity())

        result = CommunicationService.batch_send(
            student_ids = student_ids,
            comm_type   = comm_type,
            extra_data  = extra_data,
            sent_by     = sent_by
        )

        print(f"📧 Batch send by user {sent_by}: "
              f"{result['data']['sent']} sent | "
              f"{result['data']['failed']} failed")

        return jsonify(result), 200

    except Exception as e:
        print(f"❌ Batch send endpoint error: {e}")
        return jsonify({
            "status":  "error",
            "message": "Internal server error"
        }), 500


@app.route('/api/communications/history', methods=['GET'])
@jwt_required()
def get_comm_history():
    """
    Get communication history with filters
    Query params:
        ?student_id=1
        &comm_type=Risk Alert
        &status=sent
        &limit=50
        &offset=0
    Returns: {
        "status": "success",
        "data": {"history": [...], "total": int}
    }
    """
    try:
        filters = {}

        if request.args.get('student_id'):
            filters['student_id'] = int(request.args.get('student_id'))
        if request.args.get('comm_type'):
            filters['comm_type']  = request.args.get('comm_type')
        if request.args.get('status'):
            filters['status']     = request.args.get('status')

        filters['limit']  = request.args.get('limit',  50, type=int)
        filters['offset'] = request.args.get('offset', 0,  type=int)

        result = CommunicationService.get_history(filters)

        if result['status'] == 'error':
            return jsonify(result), 500

        return jsonify(result), 200

    except Exception as e:
        print(f"❌ Comm history endpoint error: {e}")
        return jsonify({
            "status":  "error",
            "message": "Internal server error"
        }), 500


@app.route('/api/communications/stats', methods=['GET'])
@jwt_required()
def get_comm_stats():
    """
    Get communication statistics
    Returns: {
        "status": "success",
        "data": {
            "total", "last_week",
            "by_type": [...],
            "by_status": [...]
        }
    }
    """
    try:
        result = CommunicationService.get_comm_stats()

        if result['status'] == 'error':
            return jsonify(result), 500

        return jsonify(result), 200

    except Exception as e:
        print(f"❌ Comm stats endpoint error: {e}")
        return jsonify({
            "status":  "error",
            "message": "Internal server error"
        }), 500


@app.route('/api/communications/templates', methods=['GET'])
@jwt_required()
def get_comm_templates():
    """
    Get all available email templates
    Returns: {
        "status": "success",
        "data": {"templates": [{name, subject, preview}]}
    }
    """
    try:
        result = CommunicationService.get_templates()
        return jsonify(result), 200

    except Exception as e:
        print(f"❌ Get templates endpoint error: {e}")
        return jsonify({
            "status":  "error",
            "message": "Internal server error"
        }), 500


@app.route('/api/students/<int:student_id>/communications', methods=['GET'])
@jwt_required()
def get_student_communications(student_id):
    """
    Get all communications for a specific student
    Query param: ?limit=20
    Returns: {"status": "success", "data": {"history": [...], "total": int}}
    """
    try:
        limit  = request.args.get('limit', 20, type=int)
        result = CommunicationService.get_history({
            'student_id': student_id,
            'limit':      limit
        })

        if result['status'] == 'error':
            return jsonify(result), 500

        return jsonify(result), 200

    except Exception as e:
        print(f"❌ Student comms endpoint error: {e}")
        return jsonify({
            "status":  "error",
            "message": "Internal server error"
        }), 500



# ================================================================
# ADVANCED ANALYTICS ROUTES - Enhancement 10
# ================================================================
from sqlalchemy import func, and_, case
from backend.database.models import (
    Student, AcademicRecord, RiskPrediction,
    BehavioralIncident, Communication, Attendance
)
from backend.database.db_config import SessionLocal

@app.route('/api/analytics/school-overview', methods=['GET'])
@jwt_required()
def get_school_overview():
    """
    School-wide KPI overview — aggregates across all modules
    Returns: {
        "status": "success",
        "data": {
            "total_students", "total_active",
            "avg_gpa", "avg_attendance",
            "risk_distribution": {Low,Medium,High,Critical},
            "grade_stats": [{grade, total, avg_gpa, avg_attendance}],
            "total_predictions", "total_incidents",
            "total_communications"
        }
    }
    """
    db = SessionLocal()
    try:
        # ── Student counts ─────────────────────────────────
        total_students = db.query(func.count(Student.id)).scalar()
        total_active   = db.query(func.count(Student.id)).filter(
            Student.is_active == True
        ).scalar()

        # ── Average GPA across all latest academic records ─
        latest_acad_subq = db.query(
            AcademicRecord.student_id,
            func.max(AcademicRecord.id).label('max_id')
        ).group_by(AcademicRecord.student_id).subquery()

        avg_gpa_row = db.query(
            func.avg(AcademicRecord.current_gpa).label('avg_gpa')
        ).join(
            latest_acad_subq,
            AcademicRecord.id == latest_acad_subq.c.max_id
        ).first()
        avg_gpa = round(float(avg_gpa_row.avg_gpa or 0), 2)

        # ── Average attendance rate ────────────────────────
        avg_att_row = db.query(
            func.avg(
                case(
                    (Attendance.status == 'present', 1),
                    else_=0
                )
            ).label('avg_att')
        ).scalar()
        avg_attendance = round(float(avg_att_row or 0) * 100, 2)

        # ── Risk distribution (latest per student) ─────────
        latest_pred_subq = db.query(
            RiskPrediction.student_id,
            func.max(RiskPrediction.id).label('max_id')
        ).group_by(RiskPrediction.student_id).subquery()

        risk_counts = db.query(
            RiskPrediction.risk_label,
            func.count().label('count')
        ).join(
            latest_pred_subq,
            RiskPrediction.id == latest_pred_subq.c.max_id
        ).group_by(RiskPrediction.risk_label).all()

        risk_dist = {'Low': 0, 'Medium': 0, 'High': 0, 'Critical': 0}
        for row in risk_counts:
            if row.risk_label in risk_dist:
                risk_dist[row.risk_label] = row.count

        # ── Grade-wise stats ───────────────────────────────
        grade_stats_rows = db.query(
            Student.grade,
            func.count(Student.id).label('total'),
            func.avg(AcademicRecord.current_gpa).label('avg_gpa')
        ).outerjoin(
            latest_acad_subq,
            Student.id == latest_acad_subq.c.student_id
        ).outerjoin(
            AcademicRecord,
            and_(
                AcademicRecord.student_id == Student.id,
                AcademicRecord.id == latest_acad_subq.c.max_id
            )
        ).filter(
            Student.is_active == True
        ).group_by(Student.grade).order_by(Student.grade).all()

        grade_stats = [
            {
                'grade':   row.grade,
                'total':   row.total,
                'avg_gpa': round(float(row.avg_gpa or 0), 2)
            }
            for row in grade_stats_rows
        ]

        # ── Section-wise GPA (for heatmap) ────────────────
        section_stats_rows = db.query(
            Student.grade,
            Student.section,
            func.count(Student.id).label('total'),
            func.avg(AcademicRecord.current_gpa).label('avg_gpa'),
            func.count(
                case((RiskPrediction.risk_label.in_(
                    ['High', 'Critical']), 1), else_=None)
            ).label('at_risk_count')
        ).outerjoin(
            latest_acad_subq,
            Student.id == latest_acad_subq.c.student_id
        ).outerjoin(
            AcademicRecord,
            and_(
                AcademicRecord.student_id == Student.id,
                AcademicRecord.id == latest_acad_subq.c.max_id
            )
        ).outerjoin(
            latest_pred_subq,
            Student.id == latest_pred_subq.c.student_id
        ).outerjoin(
            RiskPrediction,
            and_(
                RiskPrediction.student_id == Student.id,
                RiskPrediction.id == latest_pred_subq.c.max_id
            )
        ).filter(
            Student.is_active == True
        ).group_by(
            Student.grade, Student.section
        ).order_by(Student.grade, Student.section).all()

        section_stats = [
            {
                'grade':         row.grade,
                'section':       row.section or 'N/A',
                'total':         row.total,
                'avg_gpa':       round(float(row.avg_gpa or 0), 2),
                'at_risk_count': row.at_risk_count or 0
            }
            for row in section_stats_rows
        ]

        # ── Total counts ───────────────────────────────────
        total_predictions    = db.query(
            func.count(RiskPrediction.student_id.distinct())
        ).scalar()

        total_incidents      = db.query(
            func.count(BehavioralIncident.id)
        ).scalar()

        total_communications = db.query(
            func.count(Communication.id)
        ).scalar()

        # ── Confidence distribution ────────────────────────
        conf_buckets = {
            '90-100%': 0, '75-89%': 0,
            '60-74%':  0, 'Below 60%': 0
        }
        conf_rows = db.query(
            RiskPrediction.confidence_score
        ).join(
            latest_pred_subq,
            RiskPrediction.id == latest_pred_subq.c.max_id
        ).all()

        for row in conf_rows:
            score = float(row.confidence_score or 0)
            if score >= 90:
                conf_buckets['90-100%'] += 1
            elif score >= 75:
                conf_buckets['75-89%']  += 1
            elif score >= 60:
                conf_buckets['60-74%']  += 1
            else:
                conf_buckets['Below 60%'] += 1

        db.close()

        return jsonify({
            "status": "success",
            "data": {
                "total_students":       total_students,
                "total_active":         total_active,
                "avg_gpa":              avg_gpa,
                "avg_attendance":       avg_attendance,
                "risk_distribution":    risk_dist,
                "grade_stats":          grade_stats,
                "section_stats":        section_stats,
                "total_predictions":    total_predictions,
                "total_incidents":      total_incidents,
                "total_communications": total_communications,
                "confidence_distribution": conf_buckets
            }
        }), 200

    except Exception as e:
        db.close()
        print(f"❌ School overview error: {e}")
        return jsonify({
            "status":  "error",
            "message": str(e)
        }), 500


@app.route('/api/analytics/trends', methods=['GET'])
@jwt_required()
def get_analytics_trends():
    """
    Time-series trend data for charts
    Returns monthly incident counts + communication counts
    Query param: ?months=6
    """
    db = SessionLocal()
    try:
        months = request.args.get('months', 6, type=int)

        from datetime import date, timedelta
        cutoff = date.today() - timedelta(days=months * 30)

        # ── Monthly incident counts ────────────────────────
        incident_trends = db.query(
            func.date_trunc('month', BehavioralIncident.incident_date)
                .label('month'),
            func.count().label('count')
        ).filter(
            BehavioralIncident.incident_date >= cutoff
        ).group_by('month').order_by('month').all()

        # ── Monthly communication counts ───────────────────
        comm_trends = db.query(
            func.date_trunc('month', Communication.sent_at)
                .label('month'),
            func.count().label('count')
        ).filter(
            Communication.sent_at >= cutoff
        ).group_by('month').order_by('month').all()

        # ── GPA trend by grade ─────────────────────────────
        gpa_by_grade = db.query(
            Student.grade,
            func.avg(AcademicRecord.current_gpa).label('avg_gpa'),
            func.min(AcademicRecord.current_gpa).label('min_gpa'),
            func.max(AcademicRecord.current_gpa).label('max_gpa')
        ).join(
            AcademicRecord,
            AcademicRecord.student_id == Student.id
        ).filter(
            Student.is_active == True
        ).group_by(Student.grade).order_by(Student.grade).all()

        db.close()

        return jsonify({
            "status": "success",
            "data": {
                "incident_trends": [
                    {
                        "month": row.month.strftime('%b %Y')
                                 if row.month else '',
                        "count": row.count
                    }
                    for row in incident_trends
                ],
                "comm_trends": [
                    {
                        "month": row.month.strftime('%b %Y')
                                 if row.month else '',
                        "count": row.count
                    }
                    for row in comm_trends
                ],
                "gpa_by_grade": [
                    {
                        "grade":   row.grade,
                        "avg_gpa": round(float(row.avg_gpa or 0), 2),
                        "min_gpa": round(float(row.min_gpa or 0), 2),
                        "max_gpa": round(float(row.max_gpa or 0), 2)
                    }
                    for row in gpa_by_grade
                ]
            }
        }), 200

    except Exception as e:
        db.close()
        print(f"❌ Analytics trends error: {e}")
        return jsonify({
            "status":  "error",
            "message": str(e)
        }), 500



# ============================================
# RUN APP
# ============================================

if __name__ == '__main__':
    print_startup_message()
    
    # Test database connection
    if test_connection():
        print("✅ Database connected - Starting server...\n")
        app.run(host='0.0.0.0', port=5000, debug=True)
    else:
        print("❌ Database connection failed - Cannot start server!\n")




