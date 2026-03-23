# backend/routes/batch_routes.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from backend.services.batch_service import BatchService

batch_bp = Blueprint('batch', __name__)


# POST /api/batch/run
@batch_bp.route('/api/batch/run', methods=['POST'])
@jwt_required()
def run_batch_predictions():
    try:
        data = request.get_json() or {}
        filters = {
            'grade':   data.get('grade'),
            'section': data.get('section'),
        }
        result = BatchService.run_batch_predictions(filters=filters)
        if 'error' in result:
            return jsonify(result), 400
        return jsonify(result), 200
    except Exception as e:
        print(f"❌ Batch run error: {e}")
        return jsonify({'error': str(e)}), 500


# GET /api/batch/predictions
@batch_bp.route('/api/batch/predictions', methods=['GET'])
@jwt_required()
def get_batch_predictions():
    try:
        filters = {
            'grade':   request.args.get('grade', type=int),
            'section': request.args.get('section'),
            'limit':   request.args.get('limit', 100, type=int),
        }
        result = BatchService.get_all_predictions(filters=filters)
        return jsonify(result), 200
    except Exception as e:
        print(f"❌ Get batch predictions error: {e}")
        return jsonify({'error': str(e)}), 500


# GET /api/batch/summary
@batch_bp.route('/api/batch/summary', methods=['GET'])
@jwt_required()
def get_batch_summary():
    try:
        result = BatchService.get_batch_summary()   # ← was get_school_risk_summary (wrong name)
        return jsonify(result), 200
    except Exception as e:
        print(f"❌ Batch summary error: {e}")
        return jsonify({'error': str(e)}), 500


# GET /api/batch/unpredicted
@batch_bp.route('/api/batch/unpredicted', methods=['GET'])
@jwt_required()
def get_unpredicted_students():
    try:
        grade  = request.args.get('grade', type=int)
        result = BatchService.get_unpredicted_students(grade=grade)
        return jsonify(result), 200
    except Exception as e:
        print(f"❌ Get unpredicted error: {e}")
        return jsonify({'error': str(e)}), 500
