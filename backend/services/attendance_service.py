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
        """
        Mark attendance for a student
        Args:
            student_id: Student database ID
            attendance_date: Date of attendance
            status: 'present', 'absent', 'late', 'excused'
            remarks: Optional notes
            marked_by: User ID who marked attendance
        """
        db = next(get_db())
        try:
            # Check if student exists
            student = db.query(Student).filter(Student.id == student_id).first()
            if not student:
                return {'error': 'Student not found'}
            
            # Check if attendance already exists for this date
            existing = db.query(Attendance).filter(
                and_(
                    Attendance.student_id == student_id,
                    Attendance.attendance_date == attendance_date
                )
            ).first()
            
            if existing:
                # Update existing
                existing.status = status
                existing.remarks = remarks
                existing.marked_by = marked_by
                existing.updated_at = datetime.utcnow()
                message = 'Attendance updated'
            else:
                # Create new
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
            
            # Get updated attendance record
            record = db.query(Attendance).filter(
                and_(
                    Attendance.student_id == student_id,
                    Attendance.attendance_date == attendance_date
                )
            ).first()
            
            return {
                'message': message,
                'attendance': record.to_dict()
            }
        except Exception as e:
            db.rollback()
            return {'error': str(e)}
        finally:
            db.close()
    
    @staticmethod
    def mark_bulk_attendance(attendance_list: List[Dict], marked_by: int = None):
        """
        Mark attendance for multiple students at once
        Args:
            attendance_list: List of dicts with student_id, date, status
            marked_by: User ID who marked attendance
        Returns: Summary of marked attendance
        """
        db = next(get_db())
        marked_count = 0
        errors = []
        
        try:
            for item in attendance_list:
                student_id = item.get('student_id')
                attendance_date = item.get('date')
                status = item.get('status')
                remarks = item.get('remarks')
                
                if not student_id or not attendance_date or not status:
                    errors.append(f"Missing data for entry: {item}")
                    continue
                
                # Convert string date to date object if needed
                if isinstance(attendance_date, str):
                    attendance_date = datetime.strptime(attendance_date, '%Y-%m-%d').date()
                
                # Check if exists
                existing = db.query(Attendance).filter(
                    and_(
                        Attendance.student_id == student_id,
                        Attendance.attendance_date == attendance_date
                    )
                ).first()
                
                if existing:
                    existing.status = status
                    existing.remarks = remarks
                    existing.marked_by = marked_by
                    existing.updated_at = datetime.utcnow()
                else:
                    attendance = Attendance(
                        student_id=student_id,
                        attendance_date=attendance_date,
                        status=status,
                        remarks=remarks,
                        marked_by=marked_by
                    )
                    db.add(attendance)
                
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
    
    @staticmethod
    def get_student_attendance(student_id: int, start_date: date = None, 
                              end_date: date = None):
        """Get attendance records for a student"""
        db = next(get_db())
        try:
            query = db.query(Attendance).filter(Attendance.student_id == student_id)
            
            if start_date:
                query = query.filter(Attendance.attendance_date >= start_date)
            if end_date:
                query = query.filter(Attendance.attendance_date <= end_date)
            
            records = query.order_by(desc(Attendance.attendance_date)).all()
            
            return [record.to_dict() for record in records]
        finally:
            db.close()
    
    @staticmethod
    def get_attendance_stats(student_id: int, days: int = 30):
        """
        Get attendance statistics for a student
        Args:
            student_id: Student ID
            days: Number of days to look back
        Returns: Stats dict with percentages
        """
        db = next(get_db())
        try:
            start_date = date.today() - timedelta(days=days)
            
            # Total days
            total = db.query(func.count(Attendance.id)).filter(
                and_(
                    Attendance.student_id == student_id,
                    Attendance.attendance_date >= start_date
                )
            ).scalar() or 0
            
            if total == 0:
                return {
                    'total_days': 0,
                    'present': 0,
                    'absent': 0,
                    'late': 0,
                    'excused': 0,
                    'attendance_rate': 0.0
                }
            
            # Present
            present = db.query(func.count(Attendance.id)).filter(
                and_(
                    Attendance.student_id == student_id,
                    Attendance.attendance_date >= start_date,
                    Attendance.status == 'present'
                )
            ).scalar() or 0
            
            # Absent
            absent = db.query(func.count(Attendance.id)).filter(
                and_(
                    Attendance.student_id == student_id,
                    Attendance.attendance_date >= start_date,
                    Attendance.status == 'absent'
                )
            ).scalar() or 0
            
            # Late
            late = db.query(func.count(Attendance.id)).filter(
                and_(
                    Attendance.student_id == student_id,
                    Attendance.attendance_date >= start_date,
                    Attendance.status == 'late'
                )
            ).scalar() or 0
            
            # Excused
            excused = db.query(func.count(Attendance.id)).filter(
                and_(
                    Attendance.student_id == student_id,
                    Attendance.attendance_date >= start_date,
                    Attendance.status == 'excused'
                )
            ).scalar() or 0
            
            # Calculate attendance rate (present + late = attended)
            attended = present + late
            attendance_rate = (attended / total * 100) if total > 0 else 0.0
            
            return {
                'total_days': total,
                'present': present,
                'absent': absent,
                'late': late,
                'excused': excused,
                'attendance_rate': round(attendance_rate, 2),
                'period_days': days
            }
        finally:
            db.close()
    
    @staticmethod
    def get_daily_attendance(attendance_date: date, grade: int = None, 
                            section: str = None):
        """
        Get attendance for all students on a specific date
        Args:
            attendance_date: Date to check
            grade: Optional grade filter
            section: Optional section filter
        """
        db = next(get_db())
        try:
            # Get all students with filters
            student_query = db.query(Student).filter(Student.is_active == True)
            
            # Apply filters only if provided
            if grade is not None:
                student_query = student_query.filter(Student.grade == grade)
                
            if section is not None:
                student_query = student_query.filter(Student.section == section)
            
            students = student_query.order_by(Student.grade, Student.section, Student.first_name).all()
            
            # Get attendance for this date
            attendance_records = db.query(Attendance).filter(
                Attendance.attendance_date == attendance_date
            ).all()
            
            # Create lookup dict
            attendance_dict = {
                att.student_id: att.to_dict() 
                for att in attendance_records
            }
            
            # Combine results
            result = []
            for student in students:
                student_dict = student.to_dict()
                student_dict['attendance'] = attendance_dict.get(
                    student.id, 
                    {'status': 'not_marked', 'attendance_date': str(attendance_date)}
                )
                result.append(student_dict)
            
            return result
            
        except Exception as e:
            return []
        finally:
            db.close()


    
    @staticmethod
    def get_low_attendance_students(threshold: float = 75.0, days: int = 30):
        """
        Get students with low attendance
        Args:
            threshold: Attendance percentage threshold (default 75%)
            days: Number of days to check
        Returns: List of students with low attendance
        """
        db = next(get_db())
        try:
            start_date = date.today() - timedelta(days=days)
            
            # Get all active students
            students = db.query(Student).filter(Student.is_active == True).all()
            
            low_attendance = []
            
            for student in students:
                stats = AttendanceService.get_attendance_stats(student.id, days)
                
                if stats['total_days'] > 0 and stats['attendance_rate'] < threshold:
                    low_attendance.append({
                        'student': student.to_dict(),
                        'attendance_stats': stats
                    })
            
            # Sort by attendance rate (lowest first)
            low_attendance.sort(key=lambda x: x['attendance_stats']['attendance_rate'])
            
            return low_attendance
        finally:
            db.close()

# Test function
if __name__ == "__main__":
    print("=" * 60)
    print("🧪 TESTING ATTENDANCE SERVICE")
    print("=" * 60)
    
    from backend.services.student_service import StudentService
    students = StudentService.get_all_students()
    
    if students:
        student_id = students[0]['id']
        print(f"\n📋 Testing attendance for student ID: {student_id}")
        
        # Test 1: Mark attendance
        print("\n1. Marking attendance for today...")
        today = date.today()
        result = AttendanceService.mark_attendance(
            student_id=student_id,
            attendance_date=today,
            status='present',
            remarks='On time'
        )
        if 'error' not in result:
            print(f"   ✅ {result['message']}")
        else:
            print(f"   ❌ {result['error']}")
        
        # Test 2: Get attendance stats
        print("\n2. Getting attendance stats (last 30 days)...")
        stats = AttendanceService.get_attendance_stats(student_id, days=30)
        print(f"   ✅ Total days: {stats['total_days']}")
        print(f"      Present: {stats['present']}, Absent: {stats['absent']}")
        print(f"      Attendance Rate: {stats['attendance_rate']}%")
        
        # Test 3: Get student attendance records
        print("\n3. Getting attendance records...")
        records = AttendanceService.get_student_attendance(student_id)
        print(f"   ✅ Found {len(records)} attendance records")
        
    else:
        print("\n❌ No students found!")
    
    print("\n" + "=" * 60)
