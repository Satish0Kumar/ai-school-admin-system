# backend/routes/analytics_routes.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import func, case
from datetime import datetime, timedelta

from backend.database.db_config import SessionLocal
from backend.database.models import (
    Student, AcademicRecord, RiskPrediction,
    BehavioralIncident, Communication, Attendance
)

analytics_bp = Blueprint('analytics', __name__)


def _db():
    db = SessionLocal()
    try:
        return db
    except Exception:
        db.close()
        raise


# ─────────────────────────────────────────────────────────────
# GET /api/analytics/school-overview
# ─────────────────────────────────────────────────────────────
@analytics_bp.route('/api/analytics/school-overview', methods=['GET'])
@jwt_required()
def get_school_overview():
    try:
        db = _db()

        # ── 1. Total active students ──────────────────────────────
        total_active = db.query(func.count(Student.id)).filter(
            Student.is_active == True
        ).scalar() or 0

        # ── 2. School avg GPA ─────────────────────────────────────
        avg_gpa_raw = db.query(
            func.avg(AcademicRecord.current_gpa)
        ).join(Student, Student.id == AcademicRecord.student_id).filter(
            Student.is_active == True
        ).scalar()
        avg_gpa = round(float(avg_gpa_raw or 0), 1)

        # ── 3. Attendance % (present / total records) ─────────────
        att_total   = db.query(func.count(Attendance.id)).join(
            Student, Student.id == Attendance.student_id
        ).filter(Student.is_active == True).scalar() or 0

        att_present = db.query(func.count(Attendance.id)).join(
            Student, Student.id == Attendance.student_id
        ).filter(
            Student.is_active == True,
            Attendance.status == 'Present'
        ).scalar() or 0

        avg_attendance = round(
            (att_present / att_total * 100) if att_total > 0 else 0.0, 1
        )

        # ── 4. Risk distribution (latest prediction per student) ──
        latest_subq = db.query(
            RiskPrediction.student_id,
            func.max(RiskPrediction.id).label('max_id')
        ).group_by(RiskPrediction.student_id).subquery()

        risk_rows = db.query(
            RiskPrediction.risk_label,
            func.count().label('cnt')
        ).join(
            latest_subq, RiskPrediction.id == latest_subq.c.max_id
        ).group_by(RiskPrediction.risk_label).all()

        risk_distribution = {'Low': 0, 'Medium': 0, 'High': 0, 'Critical': 0}
        for row in risk_rows:
            if row.risk_label in risk_distribution:
                risk_distribution[row.risk_label] = row.cnt

        total_predictions = sum(risk_distribution.values())

        # ── 5. Confidence distribution ────────────────────────────
        conf_rows = db.query(RiskPrediction.confidence_score).join(
            latest_subq, RiskPrediction.id == latest_subq.c.max_id
        ).all()

        conf_dist = {'90-100%': 0, '75-89%': 0, '60-74%': 0, '<60%': 0}
        for (c,) in conf_rows:
            v = float(c or 0)
            if   v >= 90: conf_dist['90-100%'] += 1
            elif v >= 75: conf_dist['75-89%']  += 1
            elif v >= 60: conf_dist['60-74%']  += 1
            else:         conf_dist['<60%']    += 1

        # ── 6. Grade stats ────────────────────────────────────────
        grade_rows = db.query(
            Student.grade,
            func.count(Student.id).label('total'),
            func.avg(AcademicRecord.current_gpa).label('avg_gpa')
        ).outerjoin(
            AcademicRecord, AcademicRecord.student_id == Student.id
        ).filter(Student.is_active == True).group_by(Student.grade).all()

        grade_stats = [
            {
                'grade':   r.grade,
                'total':   r.total,
                'avg_gpa': round(float(r.avg_gpa or 0), 1)
            }
            for r in sorted(grade_rows, key=lambda x: x.grade)
        ]

        # ── 7. GPA min/max/avg per grade (for trends tab) ─────────
        gpa_by_grade = []
        for r in grade_rows:
            mm = db.query(
                func.min(AcademicRecord.current_gpa),
                func.max(AcademicRecord.current_gpa)
            ).join(Student, Student.id == AcademicRecord.student_id).filter(
                Student.grade == r.grade, Student.is_active == True
            ).first()
            gpa_by_grade.append({
                'grade':   r.grade,
                'avg_gpa': round(float(r.avg_gpa or 0), 1),
                'min_gpa': round(float(mm[0] or 0), 1),
                'max_gpa': round(float(mm[1] or 0), 1)
            })
        gpa_by_grade.sort(key=lambda x: x['grade'])

        # ── 8. Section stats ──────────────────────────────────────
        section_rows = db.query(
            Student.grade,
            Student.section,
            func.count(Student.id).label('total'),
            func.avg(AcademicRecord.current_gpa).label('avg_gpa')
        ).outerjoin(
            AcademicRecord, AcademicRecord.student_id == Student.id
        ).filter(Student.is_active == True).group_by(
            Student.grade, Student.section
        ).all()

        # at-risk count per section
        at_risk_rows = db.query(
            Student.grade,
            Student.section,
            func.count(Student.id).label('at_risk')
        ).join(
            latest_subq, Student.id == latest_subq.c.student_id
        ).join(
            RiskPrediction, RiskPrediction.id == latest_subq.c.max_id
        ).filter(
            Student.is_active == True,
            RiskPrediction.risk_label.in_(['High', 'Critical'])
        ).group_by(Student.grade, Student.section).all()

        at_risk_map = {(r.grade, r.section): r.at_risk for r in at_risk_rows}

        section_stats = [
            {
                'grade':         r.grade,
                'section':       r.section,
                'total':         r.total,
                'avg_gpa':       round(float(r.avg_gpa or 0), 1),
                'at_risk_count': at_risk_map.get((r.grade, r.section), 0)
            }
            for r in section_rows
        ]

        # ── 9. Total incidents & communications ───────────────────
        total_incidents      = db.query(
            func.count(BehavioralIncident.id)
        ).scalar() or 0

        total_communications = db.query(
            func.count(Communication.id)
        ).scalar() or 0

        db.close()

        return jsonify({
            'status': 'success',
            'data': {
                'total_active':            total_active,
                'avg_gpa':                 avg_gpa,
                'avg_attendance':          avg_attendance,
                'risk_distribution':       risk_distribution,
                'total_predictions':       total_predictions,
                'confidence_distribution': conf_dist,
                'grade_stats':             grade_stats,
                'gpa_by_grade':            gpa_by_grade,
                'section_stats':           section_stats,
                'total_incidents':         total_incidents,
                'total_communications':    total_communications
            }
        }), 200

    except Exception as e:
        print(f"❌ School overview error: {e}")
        return jsonify({'error': 'Internal server error'}), 500


# ─────────────────────────────────────────────────────────────
# GET /api/analytics/trends
# ─────────────────────────────────────────────────────────────
@analytics_bp.route('/api/analytics/trends', methods=['GET'])
@jwt_required()
def get_analytics_trends():
    try:
        months = request.args.get('months', 6, type=int)
        db     = _db()
        cutoff = datetime.utcnow() - timedelta(days=months * 30)

        # Incident trend per month
        inc_rows = db.query(
            func.to_char(BehavioralIncident.created_at, 'Mon YYYY').label('month'),
            func.count().label('count')
        ).filter(
            BehavioralIncident.created_at >= cutoff
        ).group_by(
            func.to_char(BehavioralIncident.created_at, 'Mon YYYY')
        ).order_by(
            func.min(BehavioralIncident.created_at)
        ).all()

        incident_trends = [{'month': r.month, 'count': r.count} for r in inc_rows]

        # Communication trend per month
        comm_rows = db.query(
            func.to_char(Communication.created_at, 'Mon YYYY').label('month'),
            func.count().label('count')
        ).filter(
            Communication.created_at >= cutoff
        ).group_by(
            func.to_char(Communication.created_at, 'Mon YYYY')
        ).order_by(
            func.min(Communication.created_at)
        ).all()

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
