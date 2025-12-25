"""
Risk Detection API Routes
"""
from flask import Blueprint, request, jsonify
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from services.model_service import ModelService
from utils.validation import validate_student_data

# Create blueprint
risk_bp = Blueprint('risk', __name__)

# Initialize model service (singleton pattern)
model_service = ModelService()


@risk_bp.route('/predict', methods=['POST'])
def predict_single():
    """
    Predict risk level for a single student
    
    POST /api/risk/predict
    Body: {student data as JSON}
    """
    try:
        # Get request data
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Validate input
        is_valid, error_msg = validate_student_data(data)
        if not is_valid:
            return jsonify({
                'success': False,
                'error': error_msg
            }), 400
        
        # Make prediction
        result = model_service.predict_risk(data)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500


@risk_bp.route('/predict-batch', methods=['POST'])
def predict_batch():
    """
    Predict risk level for multiple students
    
    POST /api/risk/predict-batch
    Body: {
        "students": [
            {student1_data},
            {student2_data},
            ...
        ]
    }
    """
    try:
        # Get request data
        data = request.get_json()
        
        if not data or 'students' not in data:
            return jsonify({
                'success': False,
                'error': 'No students array provided'
            }), 400
        
        students = data.get('students', [])
        
        if not students or len(students) == 0:
            return jsonify({
                'success': False,
                'error': 'Students array is empty'
            }), 400
        
        # Process each student
        results = []
        errors = []
        
        for idx, student in enumerate(students):
            # Validate
            is_valid, error_msg = validate_student_data(student)
            if not is_valid:
                errors.append({
                    'student_index': idx,
                    'student_id': student.get('student_id', f'Student_{idx}'),
                    'error': error_msg
                })
                continue
            
            # Predict
            result = model_service.predict_risk(student)
            result['student_index'] = idx
            
            if 'student_id' in student:
                result['student_id'] = student['student_id']
            
            results.append(result)
        
        return jsonify({
            'success': True,
            'total_students': len(students),
            'successful_predictions': len(results),
            'failed_predictions': len(errors),
            'predictions': results,
            'errors': errors
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500


@risk_bp.route('/model-info', methods=['GET'])
def get_model_info():
    """
    Get model information and performance metrics
    
    GET /api/risk/model-info
    """
    try:
        info = model_service.get_model_info()
        return jsonify({
            'success': True,
            'model_info': info
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
