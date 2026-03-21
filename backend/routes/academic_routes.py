# backend/routes/academic_routes.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt

from backend.services.academic_service import AcademicService
from backend.services.notification_service import NotificationService

academic_bp = Blueprint('academics', __name__)


# GET /api/students/<student_id>/academics
@academic_bp.route('/api/students/<int:student_id>/academics', methods=['GET'])
@jwt_required()
def get_student_academics(student_id):
    try:
        records = AcademicService.get_student_academic_records(student_id)
        return jsonify(records), 200
    except Exception as e:
        print(f"❌ Get academics error: {e}")
        return jsonify({'error': 'Internal server error'}), 500


# GET /api/students/<student_id>/academics/latest
@academic_bp.route('/api/students/<int:student_id>/academics/latest', methods=['GET'])
@jwt_required()
def get_student_latest_academic(student_id):
    try:
        record = AcademicService.get_latest_academic_record(student_id)
        if 'error' in record:
            return jsonify(record), 404
        return jsonify(record), 200
    except Exception as e:
        print(f"❌ Get latest academic error: {e}")
        return jsonify({'error': 'Internal server error'}), 500


# POST /api/academics
@academic_bp.route('/api/academics', methods=['POST'])
@jwt_required()
def create_academic_record():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        required = ['student_id', 'semester', 'current_gpa']
        if not all(field in data for field in required):
            return jsonify({'error': 'Missing required fields: student_id, semester, current_gpa'}), 400

        result = AcademicService.create_academic_record(data)
        if 'error' in result:
            return jsonify(result), 400

        print(f"✅ Academic record created: Student {result['student_id']} - {result['semester']}")

        # Auto-trigger parent notification
        try:
            notif_results = NotificationService.check_and_notify_academic(
                student_id        = result['student_id'],
                academic_record_id = result.get('id')
            )
            print(f"📨 Notification check: {notif_results}")
        except Exception as notif_err:
            print(f"⚠️ Notification error (non-critical): {notif_err}")

        return jsonify(result), 201
    except Exception as e:
        print(f"❌ Create academic record error: {e}")
        return jsonify({'error': 'Internal server error'}), 500


# GET /api/academics/<record_id>
@academic_bp.route('/api/academics/<int:record_id>', methods=['GET'])
@jwt_required()
def get_academic_record(record_id):
    try:
        record = AcademicService.get_academic_record(record_id)
        if 'error' in record:
            return jsonify(record), 404
        return jsonify(record), 200
    except Exception as e:
        print(f"❌ Get academic record error: {e}")
        return jsonify({'error': 'Internal server error'}), 500


# PUT /api/academics/<record_id>
@academic_bp.route('/api/academics/<int:record_id>', methods=['PUT'])
@jwt_required()
def update_academic_record(record_id):
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


# DELETE /api/academics/<record_id>
@academic_bp.route('/api/academics/<int:record_id>', methods=['DELETE'])
@jwt_required()
def delete_academic_record(record_id):
    try:
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
