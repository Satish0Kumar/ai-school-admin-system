# backend/routes/communication_routes.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

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
        sent_by = get_jwt_identity()
        result  = CommunicationService.send_communication(data, sent_by=sent_by)
        if result.get('status') == 'error':
            return jsonify(result), 400
        return jsonify(result), 200
    except Exception as e:
        print(f"❌ Send communication error: {e}")
        return jsonify({'error': str(e)}), 500


# POST /api/communications/batch
@communication_bp.route('/api/communications/batch', methods=['POST'])
@jwt_required()
def send_batch_communications():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        sent_by     = get_jwt_identity()
        student_ids = data.get('student_ids', [])
        comm_type   = data.get('communication_type', 'Risk Alert')
        extra_data  = data.get('extra_data', {})
        result = CommunicationService.batch_send(
            student_ids = student_ids,
            comm_type   = comm_type,
            extra_data  = extra_data,
            sent_by     = sent_by
        )
        if result.get('status') == 'error':
            return jsonify(result), 400
        return jsonify(result), 200
    except Exception as e:
        print(f"❌ Batch communication error: {e}")
        return jsonify({'error': str(e)}), 500


# GET /api/communications/history
@communication_bp.route('/api/communications/history', methods=['GET'])
@jwt_required()
def get_communication_history():
    try:
        filters = {
            'limit':  request.args.get('limit', 50, type=int),
            'offset': request.args.get('offset', 0,  type=int),
        }
        if request.args.get('student_id'):
            filters['student_id'] = request.args.get('student_id', type=int)
        if request.args.get('status'):
            filters['status'] = request.args.get('status')
        result = CommunicationService.get_history(filters=filters)
        return jsonify(result), 200
    except Exception as e:
        print(f"❌ Get comm history error: {e}")
        return jsonify({'error': str(e)}), 500


# GET /api/communications/stats
@communication_bp.route('/api/communications/stats', methods=['GET'])
@jwt_required()
def get_communication_stats():
    try:
        result = CommunicationService.get_comm_stats()   # ← was get_communication_stats
        return jsonify(result), 200
    except Exception as e:
        print(f"❌ Get comm stats error: {e}")
        return jsonify({'error': str(e)}), 500


# GET /api/communications/templates
@communication_bp.route('/api/communications/templates', methods=['GET'])
@jwt_required()
def get_email_templates():
    try:
        result = CommunicationService.get_templates()    # ← was get_email_templates
        return jsonify(result), 200
    except Exception as e:
        print(f"❌ Get templates error: {e}")
        return jsonify({'error': str(e)}), 500


# GET /api/students/<student_id>/communications
@communication_bp.route('/api/students/<int:student_id>/communications', methods=['GET'])
@jwt_required()
def get_student_communications(student_id):
    try:
        filters = {
            'student_id': student_id,
            'limit':      request.args.get('limit', 20, type=int)
        }
        result = CommunicationService.get_history(filters=filters)
        return jsonify(result), 200
    except Exception as e:
        print(f"❌ Get student comms error: {e}")
        return jsonify({'error': str(e)}), 500
