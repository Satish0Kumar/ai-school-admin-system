# backend/routes/marks_routes.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from backend.services.marks_service import MarksService

marks_bp = Blueprint('marks', __name__)


# POST /api/marks/entry
@marks_bp.route('/api/marks/entry', methods=['POST'])
@jwt_required()
def enter_marks():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        entered_by = get_jwt_identity()
        result = MarksService.enter_marks(data, entered_by)
        if result.get('status') == 'error':
            return jsonify(result), 400
        return jsonify(result), 201
    except Exception as e:
        print(f"❌ Enter marks error: {e}")
        return jsonify({'error': 'Internal server error'}), 500


# GET /api/marks/<grade>/<section>
@marks_bp.route('/api/marks/<int:grade>/<section>', methods=['GET'])
@jwt_required()
def get_class_marks(grade, section):
    try:
        subject  = request.args.get('subject')
        semester = request.args.get('semester')
        result   = MarksService.get_class_marks(
            grade    = grade,
            section  = section,
            subject  = subject,
            semester = semester
        )
        return jsonify(result), 200
    except Exception as e:
        print(f"❌ Get class marks error: {e}")
        return jsonify({'error': 'Internal server error'}), 500


# PUT /api/marks/<record_id>
@marks_bp.route('/api/marks/<int:record_id>', methods=['PUT'])
@jwt_required()
def update_marks(record_id):
    try:
        data   = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        result = MarksService.update_marks(record_id, data)
        if result.get('status') == 'error':
            return jsonify(result), 404
        return jsonify(result), 200
    except Exception as e:
        print(f"❌ Update marks error: {e}")
        return jsonify({'error': 'Internal server error'}), 500


# GET /api/marks/stats/<grade>
@marks_bp.route('/api/marks/stats/<int:grade>', methods=['GET'])
@jwt_required()
def get_grade_marks_stats(grade):
    try:
        section = request.args.get('section')
        result  = MarksService.get_marks_stats(grade=grade, section=section)
        return jsonify(result), 200
    except Exception as e:
        print(f"❌ Get grade stats error: {e}")
        return jsonify({'error': 'Internal server error'}), 500


# GET /api/marks/failed
@marks_bp.route('/api/marks/failed', methods=['GET'])
@jwt_required()
def get_failed_students():
    try:
        grade    = request.args.get('grade', type=int)
        semester = request.args.get('semester')
        result   = MarksService.identify_failed_students(
            grade    = grade,
            semester = semester
        )
        return jsonify(result), 200
    except Exception as e:
        print(f"❌ Get failed students error: {e}")
        return jsonify({'error': 'Internal server error'}), 500
