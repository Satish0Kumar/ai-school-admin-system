# backend/routes/student_routes.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt

from backend.services.student_service import StudentService

student_bp = Blueprint('students', __name__)


# GET /api/students
@student_bp.route('/api/students', methods=['GET'])
@jwt_required()
def get_students():
    try:
        grade   = request.args.get('grade', type=int)
        section = request.args.get('section')
        search  = request.args.get('search')

        if search:
            students = StudentService.search_students(search)
        else:
            students = StudentService.get_all_students(grade=grade, section=section)

        return jsonify(students), 200
    except Exception as e:
        print(f"❌ Get students error: {e}")
        return jsonify({'error': 'Internal server error'}), 500


# GET /api/students/count
@student_bp.route('/api/students/count', methods=['GET'])
@jwt_required()
def get_students_count():
    try:
        grade  = request.args.get('grade', type=int)
        result = StudentService.get_students_count(grade=grade)
        return jsonify(result), 200
    except Exception as e:
        print(f"❌ Get students count error: {e}")
        return jsonify({'error': 'Internal server error'}), 500


# GET /api/students/<student_id>
@student_bp.route('/api/students/<int:student_id>', methods=['GET'])
@jwt_required()
def get_student(student_id):
    try:
        student = StudentService.get_student(student_id)
        if 'error' in student:
            return jsonify(student), 404
        return jsonify(student), 200
    except Exception as e:
        print(f"❌ Get student error: {e}")
        return jsonify({'error': 'Internal server error'}), 500


# GET /api/students/<student_id>/details
@student_bp.route('/api/students/<int:student_id>/details', methods=['GET'])
@jwt_required()
def get_student_details(student_id):
    try:
        student = StudentService.get_student_with_records(student_id)
        if 'error' in student:
            return jsonify(student), 404
        return jsonify(student), 200
    except Exception as e:
        print(f"❌ Get student details error: {e}")
        return jsonify({'error': 'Internal server error'}), 500


# POST /api/students
@student_bp.route('/api/students', methods=['POST'])
@jwt_required()
def create_student():
    try:
        claims = get_jwt()
        if claims.get('role') not in ['admin', 'teacher']:
            return jsonify({'error': 'Admin or Teacher access required'}), 403

        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

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


# PUT /api/students/<student_id>
@student_bp.route('/api/students/<int:student_id>', methods=['PUT'])
@jwt_required()
def update_student(student_id):
    try:
        claims = get_jwt()
        if claims.get('role') not in ['admin', 'teacher']:
            return jsonify({'error': 'Admin or Teacher access required'}), 403

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


# DELETE /api/students/<student_id>
@student_bp.route('/api/students/<int:student_id>', methods=['DELETE'])
@jwt_required()
def delete_student(student_id):
    try:
        claims = get_jwt()
        if claims.get('role') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403

        permanent  = request.args.get('permanent', 'false').lower() == 'true'
        soft_delete = not permanent

        result = StudentService.delete_student(student_id, soft_delete=soft_delete)
        if 'error' in result:
            return jsonify(result), 404

        print(f"✅ Student {'deactivated' if soft_delete else 'deleted'}: ID {student_id}")
        return jsonify(result), 200
    except Exception as e:
        print(f"❌ Delete student error: {e}")
        return jsonify({'error': 'Internal server error'}), 500
