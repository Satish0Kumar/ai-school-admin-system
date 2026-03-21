# backend/routes/prediction_routes.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from backend.services.prediction_service import PredictionService
from backend.services.notification_service import NotificationService

prediction_bp = Blueprint('predictions', __name__)


# POST /api/students/<student_id>/predict
@prediction_bp.route('/api/students/<int:student_id>/predict', methods=['POST'])
@jwt_required()
def predict_student_risk(student_id):
    try:
        user_id = int(get_jwt_identity())
        result  = PredictionService.make_prediction(student_id, predicted_by=user_id)

        if 'error' in result:
            return jsonify(result), 400

        print(f"✅ Prediction made for student {student_id}: {result['risk_label']} ({result['confidence_score']:.1f}%)")

        # Auto-trigger high risk notification
        try:
            notif_result = NotificationService.check_and_notify_risk(
                student_id   = student_id,
                prediction_id = result.get('id'),
                risk_label   = result.get('risk_label', 'Low')
            )
            print(f"📨 Risk notification: {notif_result}")
        except Exception as notif_err:
            print(f"⚠️ Risk notification error (non-critical): {notif_err}")

        return jsonify(result), 201
    except Exception as e:
        print(f"❌ Prediction error: {e}")
        return jsonify({'error': 'Internal server error'}), 500


# GET /api/students/<student_id>/predictions
@prediction_bp.route('/api/students/<int:student_id>/predictions', methods=['GET'])
@jwt_required()
def get_student_prediction_history(student_id):
    try:
        limit       = request.args.get('limit', 10, type=int)
        predictions = PredictionService.get_student_predictions(student_id, limit=limit)
        return jsonify(predictions), 200
    except Exception as e:
        print(f"❌ Get predictions error: {e}")
        return jsonify({'error': 'Internal server error'}), 500


# GET /api/students/<student_id>/predictions/latest
@prediction_bp.route('/api/students/<int:student_id>/predictions/latest', methods=['GET'])
@jwt_required()
def get_student_latest_prediction(student_id):
    try:
        prediction = PredictionService.get_latest_prediction(student_id)
        if 'error' in prediction:
            return jsonify(prediction), 404
        return jsonify(prediction), 200
    except Exception as e:
        print(f"❌ Get latest prediction error: {e}")
        return jsonify({'error': 'Internal server error'}), 500


# GET /api/predictions/high-risk
@prediction_bp.route('/api/predictions/high-risk', methods=['GET'])
@jwt_required()
def get_high_risk_students():
    try:
        grade    = request.args.get('grade', type=int)
        students = PredictionService.get_high_risk_students(grade=grade)
        return jsonify(students), 200
    except Exception as e:
        print(f"❌ Get high-risk students error: {e}")
        return jsonify({'error': 'Internal server error'}), 500
