# backend/routes/analytics_routes.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from backend.services.prediction_service import PredictionService
from backend.services.student_service import StudentService
from backend.services.batch_service import BatchService

analytics_bp = Blueprint('analytics', __name__)


# GET /api/analytics/school-overview
@analytics_bp.route('/api/analytics/school-overview', methods=['GET'])
@jwt_required()
def get_school_overview():
    try:
        summary  = BatchService.get_school_risk_summary()
        count    = StudentService.get_students_count()
        return jsonify({
            'total_students' : count.get('count', 0),
            'risk_summary'   : summary
        }), 200
    except Exception as e:
        print(f"❌ School overview error: {e}")
        return jsonify({'error': 'Internal server error'}), 500


# GET /api/analytics/trends
@analytics_bp.route('/api/analytics/trends', methods=['GET'])
@jwt_required()
def get_analytics_trends():
    try:
        grade   = request.args.get('grade', type=int)
        students = PredictionService.get_high_risk_students(grade=grade)
        return jsonify({'trends': students}), 200
    except Exception as e:
        print(f"❌ Analytics trends error: {e}")
        return jsonify({'error': 'Internal server error'}), 500
