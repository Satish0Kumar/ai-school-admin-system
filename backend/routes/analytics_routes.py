# backend/routes/analytics_routes.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import func
from backend.database.db_config import SessionLocal
from backend.database.models import (
    Student, AcademicRecord, RiskPrediction,
    BehavioralIncident, Communication
)
from backend.services.batch_service import BatchService
from backend.services.prediction_service import PredictionService

analytics_bp = Blueprint('analytics', __name__)


def _get_db():
    db = SessionLocal()
    try:
        return db
    except Exception:
        db.close()
        raise


# GET /api/analytics/school-overview
@analytics_bp.route('/api/analytics/school-overview', methods=['GET'])
@jwt_required()
def get_school_overview():
    try:
        db = _get_db()

        # ── Total active students ──────────────────────────────────
        total_active = db.query(func.count(Student.id)).filter(
            Student.is_active == True
        ).scalar() or 0

        # ── School-wide avg GPA & attendance ──────────────────────
        gpa_row = db.query(
            func.avg(AcademicRecord.current_gpa),
            func.avg(AcademicRecord.attendance_percentage)
        ).join(Student, Student.id == AcademicRecord.student_id).filter(
            Student.is_active == True
        ).first()

        avg_gpa        = round(float(gpa_row[0] or 0), 1)
        avg_attendance = round(float(gpa_row[1] or 0), 1)

        # ── Risk distribution from latest predictions ─────────────
        latest_subq = db.query(
            RiskPrediction.student_id,
            func.max(RiskPrediction.id).label('max_id')
        ).group_by(RiskPrediction.student_id).subquery()

        risk_counts = db.query(
            RiskPrediction.risk_label,
            func.count().label('cnt')
        ).join(
            latest_subq, RiskPrediction.id == latest_subq.c.max_id
        ).group_by(RiskPrediction.risk_label).all()

        risk_distribution = {'Low': 0, 'Medium': 0, 'High': 0, 'Critical': 0}
        for row in risk_counts:
            if row.risk_label in risk_distribution:
                risk_distribution[row.risk_label] = row.cnt

        total_predictions = sum(risk_distribution.values())

        # ── Confidence distribution ────────────────────────────────
        conf_rows = db.query(RiskPrediction.confidence_score).join(
            latest_subq, RiskPrediction.id == latest_subq.c.max_id
        ).all()

        conf_distribution = {
            '90-100%': 0, '75-89%': 0, '60-74%': 0, '<60%': 0
        }
        for (c,) in conf_rows:
            v = float(c or 0)
            if v >= 90:   conf_distribution['90-100%'] += 1
            elif v >= 75: conf_distribution['75-89%']  += 1
            elif v >= 60: conf_distribution['60-74%']  += 1
            else:         conf_distribution['<60%']    += 1

        # ── Grade stats ───────────────────────────────────────────
        grade_rows = db.query(
            Student.grade,
            func.count(Student.id).label('total'),
            func.avg(AcademicRecord.current_gpa).label('avg_gpa')
        ).join(
            AcademicRecord, AcademicRecord.student_id == Student.id,
            isouter=True
        ).filter(Student.is_active == True).group_by(Student.grade).all()

        grade_stats = [
            {
                'grade':   row.grade,
                'total':   row.total,
                'avg_gpa': round(float(row.avg_gpa or 0), 1)
            }
            for row in sorted(grade_rows, key=lambda r: r.grade)
        ]

        # ── GPA by grade with min/max (for trends endpoint) ───────
        gpa_by_grade = []
        for row in grade_rows:
            minmax = db.query(
                func.min(AcademicRecord.current_gpa),
                func.max(AcademicRecord.current_gpa)
            ).join(Student, Student.id == AcademicRecord.student_id).filter(
                Student.grade == row.grade, Student.is_active == True
            ).first()
            gpa_by_grade.append({
                'grade':   row.grade,
                'avg_gpa': round(float(row.avg_gpa or 0), 1),
                'min_gpa': round(float(minmax[0] or 0), 1),
                'max_gpa': round(float(minmax[1] or 0), 1)
            })

        # ── Section stats ─────────────────────────────────────────
        section_rows = db.query(
            Student.grade,
            Student.section,
            func.count(Student.id).label('total'),
            func.avg(AcademicRecord.current_gpa).label('avg_gpa')
        ).join(
            AcademicRecord, AcademicRecord.student_id == Student.id,
            isouter=True
        ).filter(Student.is_active == True).group_by(
            Student.grade, Student.section
        ).all()

        # Count at-risk per section
        at_risk_subq = db.query(
            Student.grade,
            Student.section,
            func.count(Student.id).label('at_risk')
        ).join(
            latest_subq, Student.id == latest_subq.c.student_id
        ).join(
            RiskPrediction,
            RiskPrediction.id == latest_subq.c.max_id
        ).filter(
            Student.is_active == True,
            RiskPrediction.risk_label.in_(['High', 'Critical'])
        ).group_by(Student.grade, Student.section).all()

        at_risk_map = {
            (r.grade, r.section): r.at_risk for r in at_risk_subq
        }

        section_stats = [
            {
                'grade':         row.grade,
                'section':       row.section,
                'total':         row.total,
                'avg_gpa':       round(float(row.avg_gpa or 0), 1),
                'at_risk_count': at_risk_map.get((row.grade, row.section), 0)
            }
            for row in section_rows
        ]

        # ── Total incidents ────────────────────────────────────────
        total_incidents = db.query(func.count(BehavioralIncident.id)).scalar() or 0

        # ── Total communications ───────────────────────────────────
        total_communications = db.query(func.count(Communication.id)).scalar() or 0

        db.close()

        return jsonify({
            'status': 'success',
            'data': {
                'total_active':           total_active,
                'avg_gpa':                avg_gpa,
                'avg_attendance':         avg_attendance,
                'risk_distribution':      risk_distribution,
                'total_predictions':      total_predictions,
                'confidence_distribution':conf_distribution,
                'grade_stats':            grade_stats,
                'gpa_by_grade':           gpa_by_grade,
                'section_stats':          section_stats,
                'total_incidents':        total_incidents,
                'total_communications':   total_communications
            }
        }), 200

    except Exception as e:
        print(f"❌ School overview error: {e}")
        return jsonify({'error': 'Internal server error'}), 500


# GET /api/analytics/trends
@analytics_bp.route('/api/analytics/trends', methods=['GET'])
@jwt_required()
def get_analytics_trends():
    try:
        months = request.args.get('months', 6, type=int)
        db     = _get_db()

        from datetime import datetime, timedelta
        from sqlalchemy import extract

        cutoff = datetime.utcnow() - timedelta(days=months * 30)

        # ── Incident trend per month ───────────────────────────────
        inc_rows = db.query(
            func.to_char(BehavioralIncident.created_at, 'Mon YYYY').label('month'),
            func.count().label('count')
        ).filter(
            BehavioralIncident.created_at >= cutoff
        ).group_by('month').order_by('month').all()

        incident_trends = [{'month': r.month, 'count': r.count} for r in inc_rows]

        # ── Communication trend per month ──────────────────────────
        comm_rows = db.query(
            func.to_char(Communication.created_at, 'Mon YYYY').label('month'),
            func.count().label('count')
        ).filter(
            Communication.created_at >= cutoff
        ).group_by('month').order_by('month').all()

        comm_trends = [{'month': r.month, 'count': r.count} for r in comm_rows]

        db.close()

        return jsonify({
            'status': 'success',
            'data': {
                'incident_trends': incident_trends,
                'comm_trends':     comm_trends,
                'months':          months
            }
        }), 200

    except Exception as e:
        print(f"❌ Analytics trends error: {e}")
        return jsonify({'error': 'Internal server error'}), 500
