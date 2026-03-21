# backend/routes/report_routes.py
import io
from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required
from datetime import datetime

from backend.services.pdf_service import PDFService

report_bp = Blueprint('reports', __name__)


# GET /api/reports/student/<student_id>
@report_bp.route('/api/reports/student/<int:student_id>', methods=['GET'])
@jwt_required()
def download_student_report(student_id):
    try:
        pdf_bytes = PDFService.generate_student_report(student_id)
        buffer    = io.BytesIO(pdf_bytes)
        buffer.seek(0)
        filename  = f"student_{student_id}_report_{datetime.now().strftime('%Y%m%d')}.pdf"
        return send_file(
            buffer,
            mimetype      = 'application/pdf',
            as_attachment = True,
            download_name = filename
        )
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        print(f"❌ Student PDF error: {e}")
        return jsonify({'error': 'Failed to generate PDF'}), 500


# GET /api/reports/grade/<grade>
@report_bp.route('/api/reports/grade/<int:grade>', methods=['GET'])
@jwt_required()
def download_grade_report(grade):
    try:
        section   = request.args.get('section')
        pdf_bytes = PDFService.generate_grade_report(grade, section=section)
        buffer    = io.BytesIO(pdf_bytes)
        buffer.seek(0)
        filename  = f"grade_{grade}_report_{datetime.now().strftime('%Y%m%d')}.pdf"
        return send_file(
            buffer,
            mimetype      = 'application/pdf',
            as_attachment = True,
            download_name = filename
        )
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        print(f"❌ Grade PDF error: {e}")
        return jsonify({'error': 'Failed to generate PDF'}), 500


# GET /api/reports/atrisk
@report_bp.route('/api/reports/atrisk', methods=['GET'])
@jwt_required()
def download_atrisk_report():
    try:
        pdf_bytes = PDFService.generate_atrisk_report()
        buffer    = io.BytesIO(pdf_bytes)
        buffer.seek(0)
        filename  = f"atrisk_report_{datetime.now().strftime('%Y%m%d')}.pdf"
        return send_file(
            buffer,
            mimetype      = 'application/pdf',
            as_attachment = True,
            download_name = filename
        )
    except Exception as e:
        print(f"❌ At-risk PDF error: {e}")
        return jsonify({'error': 'Failed to generate PDF'}), 500


# GET /api/reports/preview/student/<student_id>
@report_bp.route('/api/reports/preview/student/<int:student_id>', methods=['GET'])
@jwt_required()
def preview_student_report(student_id):
    try:
        pdf_bytes = PDFService.generate_student_report(student_id)
        buffer    = io.BytesIO(pdf_bytes)
        buffer.seek(0)
        return send_file(
            buffer,
            mimetype      = 'application/pdf',
            as_attachment = False
        )
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        print(f"❌ Preview PDF error: {e}")
        return jsonify({'error': 'Failed to generate PDF'}), 500
