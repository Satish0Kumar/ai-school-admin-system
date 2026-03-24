# backend/routes/attendance_routes.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from datetime import datetime

from backend.services.attendance_service import AttendanceService

attendance_bp = Blueprint('attendance', __name__)


# POST /api/attendance/mark
@attendance_bp.route('/api/attendance/mark', methods=['POST'])
@jwt_required()
def mark_attendance():
    try:
        claims = get_jwt()
        if claims.get('role') not in ['admin', 'teacher']:
            return jsonify({'error': 'Admin or Teacher access required'}), 403

        data = request.get_json()
        required = ['student_id', 'date', 'status']
        if not all(field in data for field in required):
            return jsonify({'error': 'Missing required fields'}), 400

        current_user = get_jwt_identity()
        result = AttendanceService.mark_attendance(
            student_id      = data['student_id'],
            attendance_date = datetime.strptime(data['date'], '%Y-%m-%d').date(),
            status          = data['status'],
            remarks         = data.get('remarks'),
            marked_by       = current_user
        )
        if 'error' in result:
            return jsonify(result), 400
        return jsonify(result), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# POST /api/attendance/bulk
@attendance_bp.route('/api/attendance/bulk', methods=['POST'])
@jwt_required()
def mark_bulk_attendance():
    try:
        data            = request.get_json()
        attendance_list = data.get('attendance_list', [])

        if not attendance_list:
            return jsonify({'error': 'No attendance data provided'}), 400

        current_user = get_jwt_identity()
        result = AttendanceService.mark_bulk_attendance(
            attendance_list = attendance_list,
            marked_by       = current_user
        )
        if 'error' in result:
            return jsonify(result), 400
        return jsonify(result), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# GET /api/students/<student_id>/attendance
@attendance_bp.route('/api/students/<int:student_id>/attendance', methods=['GET'])
@jwt_required()
def get_student_attendance(student_id):
    try:
        start_date = request.args.get('start_date')
        end_date   = request.args.get('end_date')

        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

        records = AttendanceService.get_student_attendance(
            student_id = student_id,
            start_date = start_date,
            end_date   = end_date
        )
        return jsonify(records), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# GET /api/students/<student_id>/attendance/stats
@attendance_bp.route('/api/students/<int:student_id>/attendance/stats', methods=['GET'])
@jwt_required()
def get_attendance_stats(student_id):
    try:
        days  = int(request.args.get('days', 30))
        stats = AttendanceService.get_attendance_stats(
            student_id = student_id,
            days       = days
        )
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# GET /api/attendance/daily
@attendance_bp.route('/api/attendance/daily', methods=['GET'])
@jwt_required()
def get_daily_attendance():
    try:
        date_str  = request.args.get('date')
        grade_str = request.args.get('grade')
        section   = request.args.get('section')

        if not date_str:
            return jsonify({'error': 'Date parameter required'}), 400

        attendance_date = datetime.strptime(date_str, '%Y-%m-%d').date()

        grade = None
        if grade_str and grade_str != 'None':
            try:
                grade = int(grade_str)
            except:
                grade = None

        if section == 'None' or not section:
            section = None

        print(f"🔍 API: date={attendance_date}, grade={grade}, section={section}")
        results = AttendanceService.get_daily_attendance(
            attendance_date = attendance_date,
            grade           = grade,
            section         = section
        )
        print(f"✅ API: Returning {len(results)} students")
        return jsonify(results), 200
    except Exception as e:
        print(f"❌ Daily attendance error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


# GET /api/attendance/low-attendance
@attendance_bp.route('/api/attendance/low-attendance', methods=['GET'])
@jwt_required()
def get_low_attendance_students():
    try:
        threshold = float(request.args.get('threshold', 75.0))
        days      = int(request.args.get('days', 30))
        results   = AttendanceService.get_low_attendance_students(
            threshold = threshold,
            days      = days
        )
        return jsonify(results), 200
    except Exception as e:
        print(f"❌ Low attendance error: {e}")
        return jsonify({'error': str(e)}), 500
