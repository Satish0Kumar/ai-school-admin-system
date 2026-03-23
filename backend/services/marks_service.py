"""
Marks Entry Service
ScholarSense - AI-Powered Academic Intelligence System
Enhancement 6: Marks Entry Module
Handles marks entry, GPA calculation, and analytics
"""

from datetime import datetime
from sqlalchemy import and_, func, desc
from backend.database.models import MarksEntry, Student, AcademicRecord
from backend.database.db_config import SessionLocal

# ============================================
# CONSTANTS
# ============================================
EXAM_TYPES = [
    'Unit Test 1', 'Unit Test 2',
    'Mid Term', 'Final Exam',
    'Assignment', 'Other'
]

SUBJECTS = ['math', 'science', 'english', 'social', 'language']

SUBJECT_LABELS = {
    'math':     'Mathematics',
    'science':  'Science',
    'english':  'English',
    'social':   'Social Studies',
    'language': 'Language'
}

PASS_MARK = 35.0   # Minimum pass mark out of 100


# ============================================
# MARKS SERVICE
# ============================================
class MarksService:
    """Marks Entry and Analytics Service"""

    @staticmethod
    def get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    # ──────────────────────────────────────────
    # CORE CALCULATION HELPERS
    # ──────────────────────────────────────────

    @staticmethod
    def calculate_gpa(math, science, english, social, language):
        """
        GPA = average of all 5 subjects
        Formula: (math + science + english + social + language) / 5
        """
        scores = [s for s in [math, science, english, social, language]
                  if s is not None]
        if not scores:
            return 0.0
        return round(sum(scores) / len(scores), 2)

    @staticmethod
    def calculate_failed_subjects(math, science, english, social, language):
        """Count subjects below PASS_MARK (35)"""
        scores = [math, science, english, social, language]
        return sum(1 for s in scores if s is not None and s < PASS_MARK)

    @staticmethod
    def calculate_total_marks(math, science, english, social, language):
        """Sum of all subject scores"""
        scores = [s for s in [math, science, english, social, language]
                  if s is not None]
        return round(sum(scores), 2) if scores else 0.0

    # ──────────────────────────────────────────
    # ENTER MARKS
    # ──────────────────────────────────────────

    @staticmethod
    def enter_marks(data: dict, entered_by: int) -> dict:
        """
        Enter marks for a student
        Auto-calculates GPA, total_marks, failed_subjects
        Also syncs to academic_records table for ML model
        Args:
            data: marks data dict
            entered_by: user ID entering marks
        Returns:
            {"status": "success", "data": {...}} or
            {"status": "error",   "message": "..."}
        """
        db = next(MarksService.get_db())
        try:
            # ── Validate required fields ───────────────────────
            required = ['student_id', 'semester', 'exam_type']
            if not all(f in data for f in required):
                return {
                    "status":  "error",
                    "message": "Missing required fields: student_id, semester, exam_type"
                }

            if data['exam_type'] not in EXAM_TYPES:
                return {
                    "status":  "error",
                    "message": f"Invalid exam_type. Must be one of: {EXAM_TYPES}"
                }

            # ── Check student exists ───────────────────────────
            student = db.query(Student).filter(
                Student.id       == data['student_id'],
                Student.is_active == True
            ).first()

            if not student:
                return {"status": "error", "message": "Student not found or inactive"}

            # ── Extract scores ─────────────────────────────────
            math     = data.get('math_score')
            science  = data.get('science_score')
            english  = data.get('english_score')
            social   = data.get('social_score')
            language = data.get('language_score')

            # ── Auto-calculate ─────────────────────────────────
            gpa             = MarksService.calculate_gpa(
                                math, science, english, social, language)
            total_marks     = MarksService.calculate_total_marks(
                                math, science, english, social, language)
            failed_subjects = MarksService.calculate_failed_subjects(
                                math, science, english, social, language)

            # ── Check for existing record (update if exists) ───
            existing = db.query(MarksEntry).filter(
                and_(
                    MarksEntry.student_id == data['student_id'],
                    MarksEntry.semester   == data['semester'],
                    MarksEntry.exam_type  == data['exam_type']
                )
            ).first()

            if existing:
                # Update existing record
                existing.math_score      = math
                existing.science_score   = science
                existing.english_score   = english
                existing.social_score    = social
                existing.language_score  = language
                existing.total_marks     = total_marks
                existing.gpa             = gpa
                existing.failed_subjects = failed_subjects
                existing.assignment_submission_rate = data.get(
                    'assignment_submission_rate', 100.0)
                existing.remarks         = data.get('remarks')
                existing.entered_by      = entered_by
                existing.updated_at      = datetime.utcnow()
                db.commit()
                db.refresh(existing)
                marks_record = existing
                action = 'updated'
            else:
                # Create new record
                marks_record = MarksEntry(
                    student_id      = data['student_id'],
                    grade           = student.grade,
                    section         = student.section,
                    semester        = data['semester'],
                    exam_type       = data['exam_type'],
                    math_score      = math,
                    science_score   = science,
                    english_score   = english,
                    social_score    = social,
                    language_score  = language,
                    total_marks     = total_marks,
                    gpa             = gpa,
                    failed_subjects = failed_subjects,
                    assignment_submission_rate = data.get(
                        'assignment_submission_rate', 100.0),
                    entered_by      = entered_by,
                    remarks         = data.get('remarks')
                )
                db.add(marks_record)
                db.commit()
                db.refresh(marks_record)
                action = 'created'

            # ── Sync to academic_records (feeds ML model) ──────
            MarksService._sync_to_academic_records(
                db, data['student_id'], data['semester'],
                gpa, failed_subjects,
                math, science, english, social, language,
                data.get('assignment_submission_rate', 100.0)
            )

            print(f"✅ Marks {action}: Student {data['student_id']} "
                  f"- {data['semester']} / {data['exam_type']} "
                  f"(GPA: {gpa})")

            return {
                "status": "success",
                "data":   marks_record.to_dict(),
                "action": action
            }

        except Exception as e:
            db.rollback()
            print(f"❌ Enter marks error: {e}")
            return {"status": "error", "message": str(e)}

    # ──────────────────────────────────────────
    # SYNC TO ACADEMIC RECORDS (ML Feed)
    # ──────────────────────────────────────────

    @staticmethod
    def _sync_to_academic_records(
        db, student_id, semester,
        gpa, failed_subjects,
        math, science, english, social, language,
        assignment_rate
    ):
        """
        Sync marks to academic_records table so ML model
        always has up-to-date data for predictions
        """
        try:
            existing = db.query(AcademicRecord).filter(
                and_(
                    AcademicRecord.student_id == student_id,
                    AcademicRecord.semester   == semester
                )
            ).first()

            if existing:
                # Fetch previous GPA for trend calculation
                prev_gpa    = float(existing.current_gpa) if existing.current_gpa else gpa
                grade_trend = round(gpa - prev_gpa, 2)

                existing.current_gpa               = gpa
                existing.previous_gpa              = prev_gpa
                existing.grade_trend               = grade_trend
                existing.failed_subjects           = failed_subjects
                existing.math_score                = math
                existing.science_score             = science
                existing.english_score             = english
                existing.social_score              = social
                existing.language_score            = language
                existing.assignment_submission_rate= assignment_rate
                existing.updated_at                = datetime.utcnow()
            else:
                new_record = AcademicRecord(
                    student_id                 = student_id,
                    semester                   = semester,
                    current_gpa                = gpa,
                    previous_gpa               = gpa,
                    grade_trend                = 0.0,
                    failed_subjects            = failed_subjects,
                    total_subjects             = 5,
                    math_score                 = math,
                    science_score              = science,
                    english_score              = english,
                    social_score               = social,
                    language_score             = language,
                    assignment_submission_rate = assignment_rate
                )
                db.add(new_record)

            db.commit()
            print(f"🔄 Academic record synced for student {student_id} / {semester}")

        except Exception as e:
            db.rollback()
            print(f"⚠️  Academic sync error (non-critical): {e}")

    # ──────────────────────────────────────────
    # GET CLASS MARKS
    # ──────────────────────────────────────────

    @staticmethod
    def get_class_marks(grade: int, section: str = None,
                        semester: str = None, exam_type: str = None) -> dict:
        """
        Get all marks for a grade/section
        Returns: list of marks with student info
        """
        db = next(MarksService.get_db())
        try:
            query = db.query(MarksEntry).join(Student).filter(
                MarksEntry.grade == grade,
                Student.is_active == True
            )

            if section:
                query = query.filter(MarksEntry.section == section)
            if semester:
                query = query.filter(MarksEntry.semester == semester)
            if exam_type:
                query = query.filter(MarksEntry.exam_type == exam_type)

            records = query.order_by(
                desc(MarksEntry.gpa)
            ).all()

            result = []
            for rank, r in enumerate(records, 1):
                row = r.to_dict()
                row['rank']         = rank
                row['student_name'] = r.student.full_name
                row['student_code'] = r.student.student_id
                result.append(row)

            return {
                "status": "success",
                "data": {
                    "marks":   result,
                    "total":   len(result),
                    "grade":   grade,
                    "section": section
                }
            }

        except Exception as e:
            print(f"❌ Get class marks error: {e}")
            return {"status": "error", "message": str(e)}

    # ──────────────────────────────────────────
    # IDENTIFY FAILED STUDENTS
    # ──────────────────────────────────────────

    @staticmethod
    def identify_failed_students(grade: int = None,
                                 semester: str = None) -> dict:
        """
        Identify students who failed 1 or more subjects
        Returns: list with subject-wise failure details
        """
        db = next(MarksService.get_db())
        try:
            query = db.query(MarksEntry).join(Student).filter(
                MarksEntry.failed_subjects > 0,
                Student.is_active == True
            )

            if grade:
                query = query.filter(MarksEntry.grade == grade)
            if semester:
                query = query.filter(MarksEntry.semester == semester)

            records = query.order_by(
                desc(MarksEntry.failed_subjects)
            ).all()

            failed_list = []
            for r in records:
                # Which subjects failed?
                failed_subs = []
                scores = {
                    'Mathematics': r.math_score,
                    'Science':     r.science_score,
                    'English':     r.english_score,
                    'Social':      r.social_score,
                    'Language':    r.language_score
                }
                for subj, score in scores.items():
                    if score is not None and float(score) < PASS_MARK:
                        failed_subs.append({
                            'subject': subj,
                            'score':   float(score),
                            'deficit': round(PASS_MARK - float(score), 2)
                        })

                row = r.to_dict()
                row['student_name']   = r.student.full_name
                row['student_code']   = r.student.student_id
                row['grade']          = r.student.grade
                row['section']        = r.student.section
                row['failed_details'] = failed_subs
                row['parent_email']   = r.student.parent_email
                failed_list.append(row)

            return {
                "status": "success",
                "data": {
                    "failed_students": failed_list,
                    "total":           len(failed_list)
                }
            }

        except Exception as e:
            print(f"❌ Identify failed students error: {e}")
            return {"status": "error", "message": str(e)}

    # ──────────────────────────────────────────
    # GET MARKS STATS (Analytics)
    # ──────────────────────────────────────────

    @staticmethod
    def get_marks_stats(grade: int, section: str = None) -> dict:
        """
        Get marks analytics for a grade/section
        Returns: averages, top performer, subject-wise analysis
        """
        db = next(MarksService.get_db())
        try:
            query = db.query(MarksEntry).join(Student).filter(
                MarksEntry.grade  == grade,
                Student.is_active == True
            )
            if section:
                query = query.filter(MarksEntry.section == section)

            records = query.all()

            if not records:
                return {
                    "status": "success",
                    "data":   {"message": "No marks data found", "total": 0}
                }

            # ── Subject averages ───────────────────────────────
            def safe_avg(values):
                valid = [float(v) for v in values if v is not None]
                return round(sum(valid) / len(valid), 2) if valid else 0.0

            subject_avgs = {
                'Mathematics': safe_avg([r.math_score     for r in records]),
                'Science':     safe_avg([r.science_score  for r in records]),
                'English':     safe_avg([r.english_score  for r in records]),
                'Social':      safe_avg([r.social_score   for r in records]),
                'Language':    safe_avg([r.language_score for r in records])
            }

            # ── Overall stats ──────────────────────────────────
            all_gpas     = [float(r.gpa) for r in records if r.gpa]
            avg_gpa      = round(sum(all_gpas) / len(all_gpas), 2) if all_gpas else 0.0
            highest_gpa  = max(all_gpas)  if all_gpas else 0.0
            lowest_gpa   = min(all_gpas)  if all_gpas else 0.0
            total_failed = sum(1 for r in records if r.failed_subjects > 0)

            # ── Top 5 performers ──────────────────────────────
            top5 = sorted(records, key=lambda r: float(r.gpa or 0), reverse=True)[:5]
            top5_list = [
                {
                    'student_name': r.student.full_name,
                    'student_code': r.student.student_id,
                    'gpa':          float(r.gpa or 0),
                    'total_marks':  float(r.total_marks or 0)
                }
                for r in top5
            ]

            # ── GPA distribution buckets ───────────────────────
            gpa_dist = {
                'Distinction (90-100)': sum(1 for g in all_gpas if g >= 90),
                'First Class (75-89)':  sum(1 for g in all_gpas if 75 <= g < 90),
                'Second Class (60-74)': sum(1 for g in all_gpas if 60 <= g < 75),
                'Pass (35-59)':         sum(1 for g in all_gpas if 35 <= g < 60),
                'Fail (Below 35)':      sum(1 for g in all_gpas if g < 35)
            }

            return {
                "status": "success",
                "data": {
                    "total_students":  len(records),
                    "avg_gpa":         avg_gpa,
                    "highest_gpa":     highest_gpa,
                    "lowest_gpa":      lowest_gpa,
                    "total_failed":    total_failed,
                    "subject_averages":subject_avgs,
                    "top_performers":  top5_list,
                    "gpa_distribution":gpa_dist,
                    "grade":           grade,
                    "section":         section
                }
            }

        except Exception as e:
            print(f"❌ Marks stats error: {e}")
            return {"status": "error", "message": str(e)}

    # ──────────────────────────────────────────
    # UPDATE MARKS
    # ──────────────────────────────────────────

    @staticmethod
    def update_marks(record_id: int, data: dict) -> dict:
        """Update an existing marks record"""
        db = next(MarksService.get_db())
        try:
            record = db.query(MarksEntry).filter(
                MarksEntry.id == record_id
            ).first()

            if not record:
                return {"status": "error", "message": "Marks record not found"}

            # Update score fields
            score_fields = [
                'math_score', 'science_score', 'english_score',
                'social_score', 'language_score',
                'assignment_submission_rate', 'remarks'
            ]
            for field in score_fields:
                if field in data:
                    setattr(record, field, data[field])

            # Recalculate derived fields
            record.gpa = MarksService.calculate_gpa(
                record.math_score,    record.science_score,
                record.english_score, record.social_score,
                record.language_score
            )
            record.total_marks = MarksService.calculate_total_marks(
                record.math_score,    record.science_score,
                record.english_score, record.social_score,
                record.language_score
            )
            record.failed_subjects = MarksService.calculate_failed_subjects(
                record.math_score,    record.science_score,
                record.english_score, record.social_score,
                record.language_score
            )
            record.updated_at = datetime.utcnow()

            db.commit()
            db.refresh(record)

            # Sync to academic records
            MarksService._sync_to_academic_records(
                db, record.student_id, record.semester,
                float(record.gpa), record.failed_subjects,
                record.math_score,    record.science_score,
                record.english_score, record.social_score,
                record.language_score,
                record.assignment_submission_rate or 100.0
            )

            print(f"✅ Marks updated: record {record_id} → GPA {record.gpa}")
            return {"status": "success", "data": record.to_dict()}

        except Exception as e:
            db.rollback()
            print(f"❌ Update marks error: {e}")
            return {"status": "error", "message": str(e)}
        
    
    @classmethod
    def get_grade_stats(cls, grade, section=None):
        """Returns avg scores per subject for a grade/section"""
        from backend.database import get_db_connection
        conn = get_db_connection()
        try:
            cur = conn.cursor()
            query = """
                SELECT
                    AVG(math_score) as math, AVG(science_score) as science,
                    AVG(english_score) as english, AVG(social_score) as social,
                    AVG(current_gpa) as gpa, COUNT(*) as total
                FROM academic_records ar
                JOIN students s ON ar.student_id = s.id
                WHERE s.grade = %s AND s.is_active = true
            """
            params = [grade]
            if section:
                query += " AND s.section = %s"
                params.append(section)
            cur.execute(query, params)
            row = cur.fetchone()
            return dict(row) if row else {}
        finally:
            conn.close()

    @classmethod
    def get_failed_students(cls, grade=None, semester=None):
        """Returns students with failed_subjects > 0"""
        from backend.database import get_db_connection
        conn = get_db_connection()
        try:
            cur = conn.cursor()
            query = """
                SELECT s.student_id, s.first_name, s.last_name, s.grade, s.section,
                    ar.failed_subjects, ar.current_gpa, ar.semester
                FROM academic_records ar
                JOIN students s ON ar.student_id = s.id
                WHERE ar.failed_subjects > 0 AND s.is_active = true
            """
            params = []
            if grade:
                query += " AND s.grade = %s"
                params.append(grade)
            if semester:
                query += " AND ar.semester = %s"
                params.append(semester)
            query += " ORDER BY ar.failed_subjects DESC"
            cur.execute(query, params)
            return [dict(r) for r in cur.fetchall()]
        finally:
            conn.close()
