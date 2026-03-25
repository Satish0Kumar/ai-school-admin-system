"""
ScholarSense - AI-Powered Academic Intelligence System
Flask REST API — Entry Point
"""
import sys
import os
from pathlib import Path
from datetime import timedelta

# ── Project root to Python path ────────────────────────────────────────
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ── Import services needed at startup ──────────────────────────────────
from backend.database.db_config import test_connection, get_database_info
from backend.services.prediction_service import PredictionService

# ── Import blueprint registrar ─────────────────────────────────────────
from backend.routes import register_blueprints

# ══════════════════════════════════════════════════════════════════════
# APP INITIALIZATION
# ══════════════════════════════════════════════════════════════════════

app = Flask(__name__)

# ── Configuration ──────────────────────────────────────────────────────
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is not set!")

JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
if not JWT_SECRET_KEY:
    raise ValueError("JWT_SECRET_KEY environment variable is not set!")

app.config['SECRET_KEY']                = SECRET_KEY
app.config['JWT_SECRET_KEY']            = JWT_SECRET_KEY
app.config['JWT_ACCESS_TOKEN_EXPIRES']  = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 3600))
app.config['JWT_ALGORITHM']             = 'HS256'
app.config['PROPAGATE_EXCEPTIONS']      = True
print(f"\n🔐 JWT Configuration:")
print(f"   Secret Key Length: {len(app.config['JWT_SECRET_KEY'])} chars")
print(f"   Token Expiry: {app.config['JWT_ACCESS_TOKEN_EXPIRES']} seconds")
print(f"   Algorithm: {app.config['JWT_ALGORITHM']}\n")

# ── Extensions ─────────────────────────────────────────────────────────
# Allow specific origins for security
allowed_origins = os.getenv('CORS_ORIGINS', 'http://localhost:3000,http://localhost:8501').split(',')
CORS(app, resources={r"/api/*": {"origins": allowed_origins}})
jwt = JWTManager(app)

# ── Register all route blueprints ──────────────────────────────────────
register_blueprints(app)

# ══════════════════════════════════════════════════════════════════════
# HEALTH CHECK
# ══════════════════════════════════════════════════════════════════════

@app.route('/api/health', methods=['GET'])
def health_check():
    db_info = get_database_info()
    return jsonify({
        'status'  : 'healthy',
        'service' : 'ScholarSense API',
        'version' : '3.0',
        'database': db_info
    }), 200

@app.before_request
def log_request():
    if request.method != 'OPTIONS':
        print(f"📨 {request.method} {request.path}")

# ══════════════════════════════════════════════════════════════════════
# JWT ERROR HANDLERS
# ══════════════════════════════════════════════════════════════════════

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    print(f"❌ JWT Error: Token expired")
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
    return jsonify({'error': 'Token verification failed'}), 401

# ══════════════════════════════════════════════════════════════════════
# STARTUP
# ══════════════════════════════════════════════════════════════════════

def print_startup_message():
    print("\n" + "=" * 70)
    print("🎓 SCHOLARSENSE - AI-POWERED ACADEMIC INTELLIGENCE SYSTEM")
    print("=" * 70)
    print(f"📡 API Server     : http://localhost:5000")
    print(f"🔐 Authentication : JWT ({app.config['JWT_ACCESS_TOKEN_EXPIRES']}s tokens)")
    print(f"💾 Database       : PostgreSQL")
    print(f"🌐 CORS           : Enabled")
    print(f"🤖 ML Model       : {'Loaded' if PredictionService.model else 'Using dummy predictions'}")
    print(f"📦 Routes         : 13 blueprint files")
    print(f"🔖 Version        : 3.0 (Refactored)")
    print("\n🔑 Default Accounts:")
    print("   Admin:   admin@scholarsense.com")
    print("   Teacher: teacher@scholarsense.com")
    print("   (Passwords configured during setup)")
    print("=" * 70 + "\n")


if __name__ == '__main__':
    if test_connection():
        print("✅ Database connected - Starting server...")
        print_startup_message()
        debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
        app.run(debug=debug_mode, host='0.0.0.0', port=5000)
    else:
        print("❌ Database connection failed!")
        sys.exit(1)
