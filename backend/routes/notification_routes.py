# backend/routes/notification_routes.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from backend.services.notification_service import NotificationService

notification_bp = Blueprint('notifications', __name__)


# GET /api/notifications
@notification_bp.route('/api/notifications', methods=['GET'])
@jwt_required()
def get_notifications():
    try:
        limit         = request.args.get('limit', 50, type=int)
        notifications = NotificationService.get_recent_notifications(limit=limit)
        return jsonify(notifications), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# GET /api/notifications/stats
@notification_bp.route('/api/notifications/stats', methods=['GET'])
@jwt_required()
def get_notification_stats():
    try:
        stats = NotificationService.get_notification_stats()
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# GET /api/students/<student_id>/notifications
@notification_bp.route('/api/students/<int:student_id>/notifications', methods=['GET'])
@jwt_required()
def get_student_notifications(student_id):
    try:
        limit         = request.args.get('limit', 20, type=int)
        notifications = NotificationService.get_student_notifications(
            student_id = student_id,
            limit      = limit
        )
        return jsonify(notifications), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# POST /api/students/<student_id>/notify
@notification_bp.route('/api/students/<int:student_id>/notify', methods=['POST'])
@jwt_required()
def send_manual_notification(student_id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        notification_type = data.get('notification_type', 'high_risk')
        message           = data.get('message', '')

        if not message:
            return jsonify({'error': 'Message is required'}), 400

        valid_types = ['low_gpa', 'high_risk', 'low_attendance', 'failed_subjects']
        if notification_type not in valid_types:
            return jsonify({'error': f'Invalid type. Must be one of: {valid_types}'}), 400

        result = NotificationService.send_manual_notification(
            student_id        = student_id,
            notification_type = notification_type,
            custom_message    = message
        )

        if result['status'] == 'sent':
            return jsonify(result), 200
        return jsonify({'error': result.get('message', 'Send failed')}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# POST /api/students/<student_id>/notify/check
@notification_bp.route('/api/students/<int:student_id>/notify/check', methods=['POST'])
@jwt_required()
def check_and_notify_student(student_id):
    try:
        results = NotificationService.check_and_notify_academic(student_id=student_id)

        sent    = [r for r in results if r.get('status') == 'sent']
        failed  = [r for r in results if r.get('status') == 'failed']
        skipped = [r for r in results if r.get('status') in ('no_trigger', 'skipped', 'cooldown')]

        return jsonify({
            'student_id'   : student_id,
            'total_checked': len(results),
            'sent'         : len(sent),
            'failed'       : len(failed),
            'skipped'      : len(skipped),
            'results'      : results
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# POST /api/notifications/bulk-check
@notification_bp.route('/api/notifications/bulk-check', methods=['POST'])
@jwt_required()
def bulk_notification_check():
    try:
        data    = request.get_json() or {}
        grade   = data.get('grade')
        section = data.get('section')

        from backend.database.db_config import SessionLocal
        from backend.database.models import Student as StudentModel

        db = SessionLocal()
        try:
            query = db.query(StudentModel).filter(StudentModel.is_active == True)
            if grade:
                query = query.filter(StudentModel.grade == grade)
            if section:
                query = query.filter(StudentModel.section == section)
            students = query.all()
            total    = len(students)
        finally:
            db.close()

        print(f"🔄 Bulk notification check: {total} students")

        summary = {'total_students': total, 'sent': 0, 'failed': 0, 'no_trigger': 0, 'skipped': 0}

        for student in students:
            results = NotificationService.check_and_notify_academic(student_id=student.id)
            for r in results:
                status = r.get('status', 'skipped')
                if   status == 'sent'      : summary['sent']       += 1
                elif status == 'failed'    : summary['failed']     += 1
                elif status == 'no_trigger': summary['no_trigger'] += 1
                else                       : summary['skipped']    += 1

        print(f"✅ Bulk check complete: {summary}")
        return jsonify(summary), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
