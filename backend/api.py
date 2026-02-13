





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

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, get_jwt
from dotenv import load_dotenv


from backend.services.student_service import StudentService
from backend.services.academic_service import AcademicService
from backend.services.prediction_service import PredictionService  # ← ADD THIS


# Load environment variables
load_dotenv()

# Import services
from backend.auth.auth_service import AuthService
from backend.database.db_config import test_connection, get_database_info

# ... rest of the code stays the same


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
    User login endpoint
    Body: {"email": "user@email.com", "password": "password123"}
    Returns: JWT token and user info
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400
        
        result = AuthService.login(email, password)
        
        if result:
            print(f"✅ Login successful: {email}")
            return jsonify(result), 200
        else:
            print(f"❌ Login failed: {email}")
            return jsonify({'error': 'Invalid credentials'}), 401
    
    except Exception as e:
        print(f"❌ Login error: {e}")
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
    print("\n🔑 Test Credentials:")
    print("   Admin:   admin@scholarsense.com / admin123")
    print("   Teacher: teacher@scholarsense.com / teacher123")
    print("=" * 70 + "\n")



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
