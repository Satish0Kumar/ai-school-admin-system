# backend/routes/marks_routes.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

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
        result = MarksService.enter_marks(data)
        if 'error' in result:
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
        if 'error' in result:
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
        semester = request.args.get('semester')
        result   = MarksService.get_grade_stats(grade=grade, semester=semester)
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
        section  = request.args.get('section')
        semester = request.args.get('semester')
        result   = MarksService.get_failed_students(
            grade    = grade,
            section  = section,
            semester = semester
        )
        return jsonify(result), 200
    except Exception as e:
        print(f"❌ Get failed students error: {e}")
        return jsonify({'error': 'Internal server error'}), 500
