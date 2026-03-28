"""
Attendance Management Service
ScholarSense - AI-Powered Academic Intelligence System
"""
from datetime import date, datetime, timedelta
from backend.database.models import Attendance, Student
from backend.database.db_config import get_db
from sqlalchemy import func, and_, desc
from typing import List, Dict, Optional

class AttendanceService:
    """Handle attendance tracking and reporting"""

    @staticmethod
    def mark_attendance(student_id: int, attendance_date: date, status: str,
                        remarks: str = None, marked_by: int = None):
        db = next(get_db())
        try:
            student = db.query(Student).filter(Student.id == student_id).first()
            if not student:
                return {'error': 'Student not found'}

            existing = db.query(Attendance).filter(
                and_(Attendance.student_id == student_id,
                     Attendance.attendance_date == attendance_date)
            ).first()

            if existing:
                existing.status     = status
                existing.remarks    = remarks
                existing.marked_by  = marked_by
                existing.updated_at = datetime.utcnow()
                message = 'Attendance updated'
            else:
                attendance = Attendance(
                    student_id=student_id,
                    attendance_date=attendance_date,
                    status=status,
                    remarks=remarks,
                    marked_by=marked_by
                )
                db.add(attendance)
                message = 'Attendance marked'

            db.commit()
            record = db.query(Attendance).filter(
                and_(Attendance.student_id == student_id,
                     Attendance.attendance_date == attendance_date)
            ).first()
            return {'message': message, 'attendance': record.to_dict()}
        except Exception as e:
            db.rollback()
            return {'error': str(e)}
        finally:
            db.close()

    @staticmethod
    def mark_bulk_attendance(attendance_list: List[Dict], marked_by: int = None):
        db = next(get_db())
        marked_count = 0
        errors = []
        try:
            for item in attendance_list:
                student_id      = item.get('student_id')
                attendance_date = item.get('date')
                status          = item.get('status')
                remarks         = item.get('remarks')

                if not student_id or not attendance_date or not status:
                    errors.append(f"Missing data for entry: {item}")
                    continue

                if isinstance(attendance_date, str):
                    attendance_date = datetime.strptime(attendance_date, '%Y-%m-%d').date()

                existing = db.query(Attendance).filter(
                    and_(Attendance.student_id == student_id,
                         Attendance.attendance_date == attendance_date)
                ).first()

                if existing:
                    existing.status     = status
                    existing.remarks    = remarks
                    existing.marked_by  = marked_by
                    existing.updated_at = datetime.utcnow()
                else:
                    db.add(Attendance(
                        student_id=student_id,
                        attendance_date=attendance_date,
                        status=status,
                        remarks=remarks,
                        marked_by=marked_by
                    ))
                marked_count += 1

            db.commit()
            return {
                'message': f'Attendance marked for {marked_count} students',
                'marked_count': marked_count,
                'errors': errors if errors else None
            }
        except Exception as e:
            db.rollback()
            return {'error': str(e)}
        finally:
            db.close()

    # ------------------------------------------------------------------
    # UPDATE a single attendance record by its primary-key ID
    # ------------------------------------------------------------------
    @staticmethod
    def update_attendance(attendance_id: int, data: dict):
        """
        Update status / remarks of an existing attendance record.
        Args:
            attendance_id : Primary key of the Attendance row
            data          : dict with 'status' and optional 'remarks'
        """
        db = next(get_db())
        try:
            record = db.query(Attendance).filter(Attendance.id == attendance_id).first()
            if not record:
                return {'error': f'Attendance record {attendance_id} not found'}

            new_status = data.get('status')
            if new_status not in ('present', 'absent', 'late', 'excused'):
                return {'error': f'Invalid status: {new_status}'}

            record.status     = new_status
            record.remarks    = data.get('remarks', record.remarks)
            record.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(record)
            return {'message': 'Attendance updated', 'attendance': record.to_dict()}
        except Exception as e:
            db.rollback()
            return {'error': str(e)}
        finally:
            db.close()

    # ------------------------------------------------------------------
    # DELETE a single attendance record by its primary-key ID
    # ------------------------------------------------------------------
    @staticmethod
    def delete_attendance(attendance_id: int):
        """
        Permanently delete an attendance record.
        Args:
            attendance_id : Primary key of the Attendance row
        """
        db = next(get_db())
        try:
            record = db.query(Attendance).filter(Attendance.id == attendance_id).first()
            if not record:
                return {'error': f'Attendance record {attendance_id} not found'}

            db.delete(record)
            db.commit()
            return {'message': f'Attendance record {attendance_id} deleted successfully'}
        except Exception as e:
            db.rollback()
            return {'error': str(e)}
        finally:
            db.close()

    @staticmethod
    def get_student_attendance(student_id: int, start_date: date = None,
                               end_date: date = None):
        db = next(get_db())
        try:
            query = db.query(Attendance).filter(Attendance.student_id == student_id)
            if start_date:
                query = query.filter(Attendance.attendance_date >= start_date)
            if end_date:
                query = query.filter(Attendance.attendance_date <= end_date)
            records = query.order_by(desc(Attendance.attendance_date)).all()
            return [r.to_dict() for r in records]
        finally:
            db.close()

    @staticmethod
    def get_attendance_stats(student_id: int, days: int = 30):
        db = next(get_db())
        try:
            start_date = date.today() - timedelta(days=days)
            total = db.query(func.count(Attendance.id)).filter(
                and_(Attendance.student_id == student_id,
                     Attendance.attendance_date >= start_date)
            ).scalar() or 0

            if total == 0:
                return {'total_days': 0, 'present': 0, 'absent': 0,
                        'late': 0, 'excused': 0, 'attendance_rate': 0.0}

            def _count(status):
                return db.query(func.count(Attendance.id)).filter(
                    and_(Attendance.student_id == student_id,
                         Attendance.attendance_date >= start_date,
                         Attendance.status == status)
                ).scalar() or 0

            present  = _count('present')
            absent   = _count('absent')
            late     = _count('late')
            excused  = _count('excused')
            attended = present + late
            rate     = round(attended / total * 100, 2) if total else 0.0

            return {'total_days': total, 'present': present, 'absent': absent,
                    'late': late, 'excused': excused, 'attendance_rate': rate,
                    'period_days': days}
        finally:
            db.close()

    @staticmethod
    def get_daily_attendance(attendance_date: date, grade: int = None,
                             section: str = None):
        db = next(get_db())
        try:
            q = db.query(Student).filter(Student.is_active == True)
            if grade   is not None: q = q.filter(Student.grade   == grade)
            if section is not None: q = q.filter(Student.section == section)
            students = q.order_by(Student.grade, Student.section, Student.first_name).all()

            att_records = db.query(Attendance).filter(
                Attendance.attendance_date == attendance_date
            ).all()
            att_dict = {a.student_id: a.to_dict() for a in att_records}

            result = []
            for s in students:
                d = s.to_dict()
                d['attendance'] = att_dict.get(
                    s.id, {'status': 'not_marked', 'attendance_date': str(attendance_date)}
                )
                result.append(d)
            return result
        except Exception as e:
            return []
        finally:
            db.close()

    @staticmethod
    def get_low_attendance_students(threshold: float = 75.0, days: int = 30):
        db = next(get_db())
        try:
            students = db.query(Student).filter(Student.is_active == True).all()
            low = []
            for s in students:
                stats = AttendanceService.get_attendance_stats(s.id, days)
                if stats['total_days'] > 0 and stats['attendance_rate'] < threshold:
                    low.append({'student': s.to_dict(), 'attendance_stats': stats})
            low.sort(key=lambda x: x['attendance_stats']['attendance_rate'])
            return low
        finally:
            db.close()
