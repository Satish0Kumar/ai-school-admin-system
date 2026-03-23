# backend/routes/incident_routes.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt

from backend.services.behavioral_service import BehavioralService as IncidentService

incident_bp = Blueprint('incidents', __name__)


# POST /api/incidents/log
@incident_bp.route('/api/incidents/log', methods=['POST'])
@jwt_required()
def log_incident():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        claims      = get_jwt()
        reporter_id = int(claims.get('user_id') or claims.get('sub') or 1)
        result      = IncidentService.log_incident(data, reporter_id=reporter_id)
        if result.get('status') == 'error':
            return jsonify(result), 400
        return jsonify(result), 201
    except Exception as e:
        print(f"❌ Log incident error: {e}")
        return jsonify({'error': 'Internal server error'}), 500


# GET /api/incidents
@incident_bp.route('/api/incidents', methods=['GET'])
@jwt_required()
def get_all_incidents():
    try:
        filters = {
            'limit': request.args.get('limit', 50, type=int)
        }
        grade     = request.args.get('grade',     type=int)
        section   = request.args.get('section')
        severity  = request.args.get('severity')
        date_from = request.args.get('date_from')
        date_to   = request.args.get('date_to')

        if grade:     filters['grade']     = grade
        if section:   filters['section']   = section
        if severity:  filters['severity']  = severity
        if date_from: filters['date_from'] = date_from
        if date_to:   filters['date_to']   = date_to

        result = IncidentService.get_incidents(filters)
        return jsonify(result), 200
    except Exception as e:
        print(f"❌ Get incidents error: {e}")
        return jsonify({'error': 'Internal server error'}), 500


# GET /api/students/<student_id>/incidents
@incident_bp.route('/api/students/<int:student_id>/incidents', methods=['GET'])
@jwt_required()
def get_student_incidents(student_id):
    try:
        limit  = request.args.get('limit', 20, type=int)
        result = IncidentService.get_student_incidents(student_id, limit=limit)
        return jsonify(result), 200
    except Exception as e:
        print(f"❌ Get student incidents error: {e}")
        return jsonify({'error': 'Internal server error'}), 500


# GET /api/incidents/stats
@incident_bp.route('/api/incidents/stats', methods=['GET'])
@jwt_required()
def get_incident_stats():
    try:
        date_range = request.args.get('date_range', '30_days')
        result     = IncidentService.get_incident_stats(date_range=date_range)
        return jsonify(result), 200
    except Exception as e:
        print(f"❌ Get incident stats error: {e}")
        return jsonify({'error': 'Internal server error'}), 500


# GET /api/incidents/trends
@incident_bp.route('/api/incidents/trends', methods=['GET'])
@jwt_required()
def get_incident_trends():
    try:
        days   = request.args.get('days', 30, type=int)
        result = IncidentService.get_incident_trends(days=days)
        return jsonify(result), 200
    except Exception as e:
        print(f"❌ Get incident trends error: {e}")
        return jsonify({'error': 'Internal server error'}), 500


# PUT /api/incidents/<incident_id>
@incident_bp.route('/api/incidents/<int:incident_id>', methods=['PUT'])
@jwt_required()
def update_incident(incident_id):
    try:
        data   = request.get_json()
        result = IncidentService.update_incident(incident_id, data)
        if result.get('status') == 'error':
            return jsonify(result), 404
        return jsonify(result), 200
    except Exception as e:
        print(f"❌ Update incident error: {e}")
        return jsonify({'error': 'Internal server error'}), 500


# DELETE /api/incidents/<incident_id>
@incident_bp.route('/api/incidents/<int:incident_id>', methods=['DELETE'])
@jwt_required()
def delete_incident(incident_id):
    try:
        claims = get_jwt()
        if claims.get('role') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        result = IncidentService.delete_incident(incident_id)
        if result.get('status') == 'error':
            return jsonify(result), 404
        return jsonify(result), 200
    except Exception as e:
        print(f"❌ Delete incident error: {e}")
        return jsonify({'error': 'Internal server error'}), 500
