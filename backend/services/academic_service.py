"""
Academic Records Management Service
ScholarSense - AI-Powered Academic Intelligence System
"""
from datetime import datetime, date
from backend.database.models import Student, AcademicRecord
from backend.database.db_config import get_db
from sqlalchemy import desc

class AcademicService:
    """Handle academic records CRUD operations"""
    
    @staticmethod
    def create_academic_record(data: dict):
        """
        Create academic record for a student
        Args: dict with academic info
        Returns: created record dict or error
        """
        db = next(get_db())
        try:
            # Verify student exists
            student = db.query(Student).filter(Student.id == data.get('student_id')).first()
            if not student:
                return {'error': 'Student not found'}
            
            # Check if record for this semester already exists
            existing = db.query(AcademicRecord).filter(
                AcademicRecord.student_id == data.get('student_id'),
                AcademicRecord.semester == data.get('semester')
            ).first()
            
            if existing:
                return {'error': f"Academic record for semester {data.get('semester')} already exists"}
            
            # Calculate grade trend if previous GPA exists
            grade_trend = None
            if data.get('current_gpa') and data.get('previous_gpa'):
                grade_trend = float(data.get('current_gpa')) - float(data.get('previous_gpa'))
            
            # Create academic record
            record = AcademicRecord(
                student_id=data.get('student_id'),
                semester=data.get('semester'),
                current_gpa=data.get('current_gpa'),
                previous_gpa=data.get('previous_gpa'),
                grade_trend=grade_trend,
                failed_subjects=data.get('failed_subjects', 0),
                total_subjects=data.get('total_subjects', 5),
                assignment_submission_rate=data.get('assignment_submission_rate'),
                math_score=data.get('math_score'),
                science_score=data.get('science_score'),
                english_score=data.get('english_score'),
                social_score=data.get('social_score'),
                language_score=data.get('language_score')
            )
            
            db.add(record)
            db.commit()
            db.refresh(record)
            
            return record.to_dict()
        except Exception as e:
            db.rollback()
            print(f"❌ Create academic record error: {e}")
            return {'error': str(e)}
        finally:
            db.close()
    
    @staticmethod
    def get_student_academic_records(student_id: int):
        """Get all academic records for a student"""
        db = next(get_db())
        try:
            records = db.query(AcademicRecord).filter(
                AcademicRecord.student_id == student_id
            ).order_by(desc(AcademicRecord.recorded_date)).all()
            
            return [record.to_dict() for record in records]
        finally:
            db.close()
    
    @staticmethod
    def get_latest_academic_record(student_id: int):
        """Get latest academic record for a student"""
        db = next(get_db())
        try:
            record = db.query(AcademicRecord).filter(
                AcademicRecord.student_id == student_id
            ).order_by(desc(AcademicRecord.recorded_date)).first()
            
            if record:
                return record.to_dict()
            return {'error': 'No academic records found'}
        finally:
            db.close()
    
    @staticmethod
    def get_academic_record(record_id: int):
        """Get specific academic record by ID"""
        db = next(get_db())
        try:
            record = db.query(AcademicRecord).filter(AcademicRecord.id == record_id).first()
            if record:
                return record.to_dict()
            return {'error': 'Academic record not found'}
        finally:
            db.close()
    
    @staticmethod
    def update_academic_record(record_id: int, data: dict):
        """Update academic record"""
        db = next(get_db())
        try:
            record = db.query(AcademicRecord).filter(AcademicRecord.id == record_id).first()
            
            if not record:
                return {'error': 'Academic record not found'}
            
            # Update allowed fields
            updatable_fields = [
                'current_gpa', 'previous_gpa', 'failed_subjects', 'total_subjects',
                'assignment_submission_rate', 'math_score', 'science_score',
                'english_score', 'social_score', 'language_score'
            ]
            
            for field in updatable_fields:
                if field in data:
                    setattr(record, field, data[field])
            
            # Recalculate grade trend
            if record.current_gpa and record.previous_gpa:
                record.grade_trend = float(record.current_gpa) - float(record.previous_gpa)
            
            record.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(record)
            
            return record.to_dict()
        except Exception as e:
            db.rollback()
            print(f"❌ Update academic record error: {e}")
            return {'error': str(e)}
        finally:
            db.close()
    
    @staticmethod
    def delete_academic_record(record_id: int):
        """Delete academic record"""
        db = next(get_db())
        try:
            record = db.query(AcademicRecord).filter(AcademicRecord.id == record_id).first()
            
            if not record:
                return {'error': 'Academic record not found'}
            
            db.delete(record)
            db.commit()
            return {'message': 'Academic record deleted successfully'}
        except Exception as e:
            db.rollback()
            print(f"❌ Delete academic record error: {e}")
            return {'error': str(e)}
        finally:
            db.close()
    
    @staticmethod
    def get_students_by_performance(grade: int = None, min_gpa: float = None, max_gpa: float = None):
        """
        Get students filtered by academic performance
        Args:
            grade: Filter by grade
            min_gpa: Minimum GPA threshold
            max_gpa: Maximum GPA threshold
        """
        db = next(get_db())
        try:
            # Subquery to get latest record for each student
            from sqlalchemy import func
            
            subquery = db.query(
                AcademicRecord.student_id,
                func.max(AcademicRecord.recorded_date).label('max_date')
            ).group_by(AcademicRecord.student_id).subquery()
            
            query = db.query(Student, AcademicRecord).join(
                AcademicRecord, Student.id == AcademicRecord.student_id
            ).join(
                subquery,
                (AcademicRecord.student_id == subquery.c.student_id) &
                (AcademicRecord.recorded_date == subquery.c.max_date)
            ).filter(Student.is_active == True)
            
            if grade:
                query = query.filter(Student.grade == grade)
            
            if min_gpa is not None:
                query = query.filter(AcademicRecord.current_gpa >= min_gpa)
            
            if max_gpa is not None:
                query = query.filter(AcademicRecord.current_gpa <= max_gpa)
            
            results = query.all()
            
            return [{
                'student': student.to_dict(),
                'academic_record': record.to_dict()
            } for student, record in results]
        finally:
            db.close()

# Test function
if __name__ == "__main__":
    print("=" * 60)
    print("🧪 TESTING ACADEMIC SERVICE")
    print("=" * 60)
    
    # Get first student to test with
    from backend.services.student_service import StudentService
    students = StudentService.get_all_students()
    
    if students:
        student_id = students[0]['id']
        print(f"\n📚 Testing with student ID: {student_id}")
        
        # Test 1: Create academic record
        print("\n1. Creating academic record...")
        test_record = {
            'student_id': student_id,
            'semester': '2026-Spring',
            'current_gpa': 85.5,
            'previous_gpa': 82.0,
            'failed_subjects': 0,
            'total_subjects': 5,
            'assignment_submission_rate': 95.0,
            'math_score': 88.0,
            'science_score': 85.0,
            'english_score': 82.0,
            'social_score': 86.0,
            'language_score': 84.0
        }
        
        result = AcademicService.create_academic_record(test_record)
        if 'error' in result:
            print(f"   ℹ️  {result['error']}")
        else:
            print(f"   ✅ Academic record created: {result['semester']} - GPA: {result['current_gpa']}")
        
        # Test 2: Get student's records
        print("\n2. Getting student's academic records...")
        records = AcademicService.get_student_academic_records(student_id)
        print(f"   ✅ Found {len(records)} academic records")
        
        # Test 3: Get latest record
        print("\n3. Getting latest academic record...")
        latest = AcademicService.get_latest_academic_record(student_id)
        if 'error' not in latest:
            print(f"   ✅ Latest: {latest['semester']} - GPA: {latest['current_gpa']}")
        
    else:
        print("\n❌ No students found. Create a student first!")
    
    print("\n" + "=" * 60)
