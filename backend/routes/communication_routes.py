# backend/routes/communication_routes.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from backend.services.communication_service import CommunicationService

communication_bp = Blueprint('communications', __name__)


# POST /api/communications/send
@communication_bp.route('/api/communications/send', methods=['POST'])
@jwt_required()
def send_communication():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        result = CommunicationService.send_email(data)
        if 'error' in result:
            return jsonify(result), 400
        return jsonify(result), 200
    except Exception as e:
        print(f"❌ Send communication error: {e}")
        return jsonify({'error': 'Internal server error'}), 500


# POST /api/communications/batch
@communication_bp.route('/api/communications/batch', methods=['POST'])
@jwt_required()
def send_batch_communications():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        result = CommunicationService.send_batch_emails(data)
        if 'error' in result:
            return jsonify(result), 400
        return jsonify(result), 200
    except Exception as e:
        print(f"❌ Batch communication error: {e}")
        return jsonify({'error': 'Internal server error'}), 500


# GET /api/communications/history
@communication_bp.route('/api/communications/history', methods=['GET'])
@jwt_required()
def get_communication_history():
    try:
        limit  = request.args.get('limit', 50, type=int)
        result = CommunicationService.get_communication_history(limit=limit)
        return jsonify(result), 200
    except Exception as e:
        print(f"❌ Get comm history error: {e}")
        return jsonify({'error': 'Internal server error'}), 500


# GET /api/communications/stats
@communication_bp.route('/api/communications/stats', methods=['GET'])
@jwt_required()
def get_communication_stats():
    try:
        result = CommunicationService.get_communication_stats()
        return jsonify(result), 200
    except Exception as e:
        print(f"❌ Get comm stats error: {e}")
        return jsonify({'error': 'Internal server error'}), 500


# GET /api/communications/templates
@communication_bp.route('/api/communications/templates', methods=['GET'])
@jwt_required()
def get_email_templates():
    try:
        result = CommunicationService.get_email_templates()
        return jsonify(result), 200
    except Exception as e:
        print(f"❌ Get templates error: {e}")
        return jsonify({'error': 'Internal server error'}), 500


# GET /api/students/<student_id>/communications
@communication_bp.route('/api/students/<int:student_id>/communications', methods=['GET'])
@jwt_required()
def get_student_communications(student_id):
    try:
        limit  = request.args.get('limit', 20, type=int)
        result = CommunicationService.get_student_communications(
            student_id = student_id,
            limit      = limit
        )
        return jsonify(result), 200
    except Exception as e:
        print(f"❌ Get student comms error: {e}")
        return jsonify({'error': 'Internal server error'}), 500
