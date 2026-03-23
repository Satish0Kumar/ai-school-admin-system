"""
Batch Risk Analysis Service
ScholarSense - AI-Powered Academic Intelligence System
Enhancement 8: Run ML predictions for all/filtered students at once
"""

from datetime import datetime
from sqlalchemy import and_, func
from backend.database.models import Student, AcademicRecord, RiskPrediction
from backend.database.db_config import SessionLocal
from backend.services.prediction_service import PredictionService

# ============================================
# CONSTANTS
# ============================================
RISK_LEVELS = ['Low', 'Medium', 'High', 'Critical']

RISK_COLORS = {
    'Low':      '#00CC44',
    'Medium':   '#FFA500',
    'High':     '#FF4B4B',
    'Critical': '#8B0000'
}


class BatchService:
    """Batch Risk Analysis Service"""

    @staticmethod
    def get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    # ──────────────────────────────────────────
    # RUN BATCH PREDICTIONS
    # ──────────────────────────────────────────

    @staticmethod
    def run_batch_predictions(filters: dict = {}, triggered_by: int = None) -> dict:
        """
        Run risk predictions for all/filtered students
        Filters: grade, section, risk_label (re-predict only specific risk levels)
        Returns: summary + per-student results
        """
        db = next(BatchService.get_db())
        try:
            # ── Build student query ────────────────────────
            query = db.query(Student).filter(Student.is_active == True)

            if 'grade' in filters and filters['grade']:
                query = query.filter(Student.grade == filters['grade'])

            if 'section' in filters and filters['section']:
                query = query.filter(Student.section == filters['section'])

            students = query.all()

            if not students:
                return {
                    "status":  "error",
                    "message": "No students found for selected filters"
                }

            print(f"🔁 Batch prediction started: {len(students)} students "
                  f"| triggered by user {triggered_by}")

            # ── Run predictions ────────────────────────────
            results     = []
            success     = 0
            failed      = 0
            skipped     = 0

            risk_summary = {r: 0 for r in RISK_LEVELS}

            for student in students:
                try:
                    # Get latest academic record
                    academic = db.query(AcademicRecord).filter(
                        AcademicRecord.student_id == student.id
                    ).order_by(
                        AcademicRecord.created_at.desc()
                    ).first()

                    if not academic:
                        # Still run prediction — PredictionService uses default values internally
                        prediction = PredictionService.make_prediction(
                            student.id,
                            predicted_by=triggered_by
                        )
                        if 'error' in prediction:
                            results.append({
                                "student_id":   student.id,
                                "student_code": student.student_id,
                                "student_name": student.full_name,
                                "grade":        student.grade,
                                "section":      student.section,
                                "status":       "skipped",
                                "reason":       prediction['error']   # will say "No academic records found"
                            })
                            skipped += 1
                        else:
                            risk_label = prediction.get('risk_label', 'Low')
                            if risk_label in risk_summary:
                                risk_summary[risk_label] += 1
                            results.append({
                                "student_id":       student.id,
                                "student_code":     student.student_id,
                                "student_name":     student.full_name,
                                "grade":            student.grade,
                                "section":          student.section,
                                "status":           "success",
                                "risk_label":       risk_label,
                                "confidence_score": prediction.get('confidence_score', 0),
                                "gpa":              0,
                                "failed_subjects":  0
                            })
                            success += 1
                        continue

                    # Run prediction via PredictionService
                    prediction = PredictionService.make_prediction(
                        student.id,
                        predicted_by=triggered_by
                    )

                    if 'error' in prediction:
                        results.append({
                            "student_id":   student.id,
                            "student_code": student.student_id,
                            "student_name": student.full_name,
                            "grade":        student.grade,
                            "section":      student.section,
                            "status":       "failed",
                            "reason":       prediction['error']
                        })
                        failed += 1
                        continue

                    # Track risk summary
                    risk_label = prediction.get('risk_label', 'Low')
                    if risk_label in risk_summary:
                        risk_summary[risk_label] += 1

                    results.append({
                        "student_id":           student.id,
                        "student_code":         student.student_id,
                        "student_name":         student.full_name,
                        "grade":                student.grade,
                        "section":              student.section,
                        "status":               "success",
                        "risk_label":           risk_label,
                        "confidence_score":     prediction.get('confidence_score',     0),
                        "probability_low":      prediction.get('probability_low',      0),
                        "probability_medium":   prediction.get('probability_medium',   0),
                        "probability_high":     prediction.get('probability_high',     0),
                        "probability_critical": prediction.get('probability_critical', 0),
                        "gpa":                  float(academic.current_gpa or 0),
                        "failed_subjects":      academic.failed_subjects or 0
                    })
                    success += 1


                except Exception as e:
                    results.append({
                        "student_id":   student.id,
                        "student_code": student.student_id,
                        "student_name": student.full_name,
                        "grade":        student.grade,
                        "section":      student.section,
                        "status":       "failed",
                        "reason":       str(e)
                    })
                    failed += 1

            total = len(students)
            print(f"✅ Batch done: {success} success | "
                  f"{skipped} skipped | {failed} failed / {total} total")

            return {
                "status": "success",
                "data": {
                    "summary": {
                        "total":        total,
                        "success":      success,
                        "skipped":      skipped,
                        "failed":       failed,
                        "risk_summary": risk_summary,
                        "run_at":       datetime.utcnow().isoformat(),
                        "triggered_by": triggered_by,
                        "filters":      filters
                    },
                    "results": results
                }
            }

        except Exception as e:
            print(f"❌ Batch prediction error: {e}")
            return {"status": "error", "message": str(e)}

    # ──────────────────────────────────────────
    # GET LATEST PREDICTIONS (No re-run)
    # ──────────────────────────────────────────

    @staticmethod
    def get_all_predictions(filters: dict = {}) -> dict:
        """
        Fetch latest existing predictions for all students
        (Does NOT re-run ML — just reads stored predictions)
        Filters: grade, section, risk_label, limit
        Returns: list of students with their latest prediction
        """
        db = next(BatchService.get_db())
        try:
            # Subquery: latest prediction ID per student
            latest_pred_subq = db.query(
                RiskPrediction.student_id,
                func.max(RiskPrediction.id).label('max_id')
            ).group_by(
                RiskPrediction.student_id
            ).subquery()

            # Main query joining students + latest prediction
            query = db.query(Student, RiskPrediction).join(
                latest_pred_subq,
                Student.id == latest_pred_subq.c.student_id
            ).join(
                RiskPrediction,
                and_(
                    RiskPrediction.student_id == Student.id,
                    RiskPrediction.id == latest_pred_subq.c.max_id
                )
            ).filter(Student.is_active == True)

            # Apply filters
            if 'grade' in filters and filters['grade']:
                query = query.filter(Student.grade == filters['grade'])

            if 'section' in filters and filters['section']:
                query = query.filter(Student.section == filters['section'])

            if 'risk_label' in filters and filters['risk_label']:
                query = query.filter(
                    RiskPrediction.risk_label == filters['risk_label']
                )

            # Sort: Critical first
            risk_order = {r: i for i, r in enumerate(
                ['Critical', 'High', 'Medium', 'Low']
            )}
            rows = query.all()

            # Sort by risk severity
            rows.sort(
                key=lambda x: risk_order.get(x[1].risk_label, 99)
            )

            # Limit
            limit = filters.get('limit', 200)
            rows  = rows[:limit]

            results = []
            for student, pred in rows:
                results.append({
                    "student_id":           student.id,
                    "student_code":         student.student_id,
                    "student_name":         student.full_name,
                    "grade":                student.grade,
                    "section":              student.section,
                    "parent_email":         student.parent_email,
                    "risk_label":           pred.risk_label,
                    "confidence_score":     float(pred.confidence_score or 0),
                    "probability_low":      float(pred.probability_low or 0),
                    "probability_medium":   float(pred.probability_medium or 0),
                    "probability_high":     float(pred.probability_high or 0),
                    "probability_critical": float(pred.probability_critical or 0),
                    "predicted_at":         pred.created_at.isoformat()
                                            if pred.created_at else None
                })

            # Risk level summary counts
            risk_summary = {r: 0 for r in RISK_LEVELS}
            for r in results:
                lbl = r.get('risk_label', 'Low')
                if lbl in risk_summary:
                    risk_summary[lbl] += 1

            return {
                "status": "success",
                "data": {
                    "students":     results,
                    "total":        len(results),
                    "risk_summary": risk_summary,
                    "filters":      filters
                }
            }

        except Exception as e:
            print(f"❌ Get all predictions error: {e}")
            return {"status": "error", "message": str(e)}

    # ──────────────────────────────────────────
    # GET STUDENTS WITHOUT PREDICTIONS
    # ──────────────────────────────────────────

    @staticmethod
    def get_unpredicted_students(grade: int = None) -> dict:
        """
        Find active students who have NO prediction yet
        Useful for identifying who needs first-time prediction
        """
        db = next(BatchService.get_db())
        try:
            # Students who have at least one prediction
            predicted_ids = db.query(
                RiskPrediction.student_id
            ).distinct().subquery()

            # Students with NO prediction
            query = db.query(Student).filter(
                Student.is_active == True,
                ~Student.id.in_(predicted_ids)
            )

            if grade:
                query = query.filter(Student.grade == grade)

            unpredicted = query.all()

            return {
                "status": "success",
                "data": {
                    "students": [
                        {
                            "student_id":   s.id,
                            "student_code": s.student_id,
                            "student_name": s.full_name,
                            "grade":        s.grade,
                            "section":      s.section
                        }
                        for s in unpredicted
                    ],
                    "total": len(unpredicted)
                }
            }

        except Exception as e:
            print(f"❌ Get unpredicted students error: {e}")
            return {"status": "error", "message": str(e)}

    # ──────────────────────────────────────────
    # GET BATCH SUMMARY STATS
    # ──────────────────────────────────────────

    @staticmethod
    def get_batch_summary() -> dict:
        """
        Get overall risk summary across all active students
        Returns: counts per risk level + school-wide stats
        """
        db = next(BatchService.get_db())
        try:
            # Latest prediction per student subquery
            latest_subq = db.query(
                RiskPrediction.student_id,
                func.max(RiskPrediction.id).label('max_id')
            ).group_by(RiskPrediction.student_id).subquery()

            risk_counts = db.query(
                RiskPrediction.risk_label,
                func.count().label('count')
            ).join(
                latest_subq,
                RiskPrediction.id == latest_subq.c.max_id
            ).group_by(RiskPrediction.risk_label).all()

            summary = {r: 0 for r in RISK_LEVELS}
            for row in risk_counts:
                if row.risk_label in summary:
                    summary[row.risk_label] = row.count

            total_active     = db.query(func.count()).filter(
                Student.is_active == True
            ).scalar()

            total_predicted  = db.query(
                func.count(RiskPrediction.student_id.distinct())
            ).scalar()

            total_unpredicted = total_active - total_predicted

            # Average confidence
            avg_conf = db.query(
                func.avg(RiskPrediction.confidence_score)
            ).join(
                latest_subq,
                RiskPrediction.id == latest_subq.c.max_id
            ).scalar()

            return {
                "status": "success",
                "data": {
                    "risk_summary":      summary,
                    "total_active":      total_active,
                    "total_predicted":   total_predicted,
                    "total_unpredicted": total_unpredicted,
                    "avg_confidence":    round(float(avg_conf), 2)
                                         if avg_conf else 0.0
                }
            }

        except Exception as e:
            print(f"❌ Batch summary error: {e}")
            return {"status": "error", "message": str(e)}
