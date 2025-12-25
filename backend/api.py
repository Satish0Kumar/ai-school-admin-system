"""
Main Flask API Application
AI-Based Smart School Administration System - Module 1
"""
from flask import Flask, jsonify
from flask_cors import CORS
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).resolve().parent))
from config.settings import API_HOST, API_PORT, DEBUG
from routes.risk_detection import risk_bp

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Register blueprints
app.register_blueprint(risk_bp, url_prefix='/api/risk')


@app.route('/')
def home():
    """API home route"""
    return jsonify({
        'success': True,
        'message': 'AI School Administration System - API',
        'module': 'Module 1: Early Warning System',
        'version': '1.0.0',
        'endpoints': {
            'health': {
                'method': 'GET',
                'path': '/api/health',
                'description': 'Health check endpoint'
            },
            'predict_single': {
                'method': 'POST',
                'path': '/api/risk/predict',
                'description': 'Predict risk for single student'
            },
            'predict_batch': {
                'method': 'POST',
                'path': '/api/risk/predict-batch',
                'description': 'Predict risk for multiple students'
            },
            'model_info': {
                'method': 'GET',
                'path': '/api/risk/model-info',
                'description': 'Get model information'
            }
        },
        'documentation': 'See README.md for API usage examples'
    }), 200


@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'success': True,
        'status': 'healthy',
        'service': 'AI School Admin API',
        'module': 'Risk Detection',
        'version': '1.0.0'
    }), 200


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found',
        'message': 'The requested URL was not found on the server'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'success': False,
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500


if __name__ == '__main__':
    print("\n" + "="*70)
    print("AI SCHOOL ADMINISTRATION SYSTEM - API SERVER")
    print("="*70)
    print(f"Module: Early Warning System (Risk Detection)")
    print(f"Version: 1.0.0")
    print(f"\nStarting server...")
    print(f"  Host: {API_HOST}")
    print(f"  Port: {API_PORT}")
    print(f"  Debug: {DEBUG}")
    print(f"\nAPI Endpoints:")
    print(f"  GET  http://{API_HOST}:{API_PORT}/")
    print(f"  GET  http://{API_HOST}:{API_PORT}/api/health")
    print(f"  POST http://{API_HOST}:{API_PORT}/api/risk/predict")
    print(f"  POST http://{API_HOST}:{API_PORT}/api/risk/predict-batch")
    print(f"  GET  http://{API_HOST}:{API_PORT}/api/risk/model-info")
    print("="*70 + "\n")
    
    # Run Flask app
    app.run(
        host=API_HOST,
        port=API_PORT,
        debug=DEBUG
    )
