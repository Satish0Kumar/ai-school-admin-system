"""
Student Management Service
ScholarSense - AI-Powered Academic Intelligence System
"""
from datetime import datetime, date
from backend.database.models import Student, AcademicRecord
from backend.database.db_config import get_db
from sqlalchemy import or_, and_

class StudentService:
    """Handle student CRUD operations"""
    
    @staticmethod
    def create_student(data: dict):
        """
        Create a new student
        Args: dict with student info
        Returns: created student dict or error
        """
        db = next(get_db())
        try:
            # Check if student ID already exists
            existing = db.query(Student).filter(Student.student_id == data.get('student_id')).first()
            if existing:
                return {'error': f"Student ID {data.get('student_id')} already exists"}
            
            # Parse date if provided as string
            dob = data.get('date_of_birth')
            if isinstance(dob, str):
                dob = datetime.strptime(dob, '%Y-%m-%d').date()
            
            # Create student
            student = Student(
                student_id=data.get('student_id'),
                first_name=data.get('first_name'),
                last_name=data.get('last_name'),
                grade=data.get('grade'),
                section=data.get('section'),
                age=data.get('age'),
                gender=data.get('gender'),
                date_of_birth=dob,
                parent_name=data.get('parent_name'),
                parent_phone=data.get('parent_phone'),
                parent_email=data.get('parent_email'),
                socioeconomic_status=data.get('socioeconomic_status', 'Medium'),
                parent_education=data.get('parent_education', 'High School'),
                is_active=True
            )
            
            db.add(student)
            db.commit()
            db.refresh(student)
            
            return student.to_dict()
        except Exception as e:
            db.rollback()
            print(f"❌ Create student error: {e}")
            return {'error': str(e)}
        finally:
            db.close()
    
    @staticmethod
    def get_student(student_id: int):
        """Get student by database ID"""
        db = next(get_db())
        try:
            student = db.query(Student).filter(Student.id == student_id).first()
            if student:
                return student.to_dict()
            return {'error': 'Student not found'}
        finally:
            db.close()
    
    @staticmethod
    def get_student_by_student_id(student_id: str):
        """Get student by student ID (e.g., 'STU2024001')"""
        db = next(get_db())
        try:
            student = db.query(Student).filter(Student.student_id == student_id).first()
            if student:
                return student.to_dict()
            return {'error': 'Student not found'}
        finally:
            db.close()
    
    @staticmethod
    def get_all_students(grade: int = None, section: str = None, is_active: bool = True):
        """
        Get all students with optional filters
        Args:
            grade: Filter by grade (6-10)
            section: Filter by section
            is_active: Show only active students
        """
        db = next(get_db())
        try:
            query = db.query(Student).filter(Student.is_active == is_active)
            
            if grade:
                query = query.filter(Student.grade == grade)
            
            if section:
                query = query.filter(Student.section == section)
            
            students = query.order_by(Student.grade, Student.section, Student.last_name).all()
            return [student.to_dict() for student in students]
        finally:
            db.close()
    
    @staticmethod
    def search_students(search_term: str):
        """
        Search students by name, student ID, or parent name
        Args: search_term (string)
        Returns: list of matching students
        """
        db = next(get_db())
        try:
            search_pattern = f"%{search_term}%"
            students = db.query(Student).filter(
                or_(
                    Student.first_name.ilike(search_pattern),
                    Student.last_name.ilike(search_pattern),
                    Student.student_id.ilike(search_pattern),
                    Student.parent_name.ilike(search_pattern)
                )
            ).filter(Student.is_active == True).limit(50).all()
            
            return [student.to_dict() for student in students]
        finally:
            db.close()
    
    @staticmethod
    def update_student(student_id: int, data: dict):
        """
        Update student information
        Args:
            student_id: Database ID
            data: dict with fields to update
        """
        db = next(get_db())
        try:
            student = db.query(Student).filter(Student.id == student_id).first()
            
            if not student:
                return {'error': 'Student not found'}
            
            # Update allowed fields
            updatable_fields = [
                'first_name', 'last_name', 'grade', 'section', 'age', 'gender',
                'date_of_birth', 'parent_name', 'parent_phone', 'parent_email',
                'socioeconomic_status', 'parent_education', 'is_active'
            ]
            
            for field in updatable_fields:
                if field in data:
                    # Handle date conversion
                    if field == 'date_of_birth' and isinstance(data[field], str):
                        data[field] = datetime.strptime(data[field], '%Y-%m-%d').date()
                    setattr(student, field, data[field])
            
            student.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(student)
            
            return student.to_dict()
        except Exception as e:
            db.rollback()
            print(f"❌ Update student error: {e}")
            return {'error': str(e)}
        finally:
            db.close()
    
    @staticmethod
    def delete_student(student_id: int, soft_delete: bool = True):
        """
        Delete or deactivate student
        Args:
            student_id: Database ID
            soft_delete: If True, just mark as inactive; if False, permanently delete
        """
        db = next(get_db())
        try:
            student = db.query(Student).filter(Student.id == student_id).first()
            
            if not student:
                return {'error': 'Student not found'}
            
            if soft_delete:
                # Soft delete - just mark as inactive
                student.is_active = False
                student.updated_at = datetime.utcnow()
                db.commit()
                return {'message': 'Student deactivated successfully'}
            else:
                # Hard delete - permanently remove (CASCADE will delete related records)
                db.delete(student)
                db.commit()
                return {'message': 'Student deleted permanently'}
        except Exception as e:
            db.rollback()
            print(f"❌ Delete student error: {e}")
            return {'error': str(e)}
        finally:
            db.close()
    
    @staticmethod
    def get_students_count(grade: int = None):
        """Get total number of students, optionally by grade"""
        db = next(get_db())
        try:
            query = db.query(Student).filter(Student.is_active == True)
            
            if grade:
                query = query.filter(Student.grade == grade)
            
            return {'count': query.count()}
        finally:
            db.close()
    
    @staticmethod
    def get_student_with_records(student_id: int):
        """
        Get student with all related records (academic, attendance, predictions)
        """
        db = next(get_db())
        try:
            student = db.query(Student).filter(Student.id == student_id).first()
            
            if not student:
                return {'error': 'Student not found'}
            
            # Get basic info
            student_data = student.to_dict()
            
            # Get academic records
            student_data['academic_records'] = [record.to_dict() for record in student.academic_records]
            
            # Get recent attendance (last 30 days)
            from datetime import timedelta
            thirty_days_ago = date.today() - timedelta(days=30)
            recent_attendance = [att.to_dict() for att in student.attendance_records 
                               if att.attendance_date >= thirty_days_ago]
            student_data['recent_attendance'] = recent_attendance
            
            # Get behavioral incidents (last 6 months)
            six_months_ago = date.today() - timedelta(days=180)
            recent_incidents = [inc.to_dict() for inc in student.incidents 
                              if inc.incident_date >= six_months_ago]
            student_data['recent_incidents'] = recent_incidents
            
            # Get latest risk prediction
            if student.predictions:
                latest_prediction = max(student.predictions, key=lambda x: x.prediction_date)
                student_data['latest_risk_prediction'] = latest_prediction.to_dict()
            else:
                student_data['latest_risk_prediction'] = None
            
            return student_data
        finally:
            db.close()

# Test functions
if __name__ == "__main__":
    print("=" * 60)
    print("🧪 TESTING STUDENT SERVICE")
    print("=" * 60)
    
    # Test 1: Create student
    print("\n1. Creating test student...")
    test_student = {
        'student_id': 'STU2026001',
        'first_name': 'Rajesh',
        'last_name': 'Kumar',
        'grade': 10,
        'section': 'A',
        'age': 15,
        'gender': 'Male',
        'date_of_birth': '2011-05-15',
        'parent_name': 'Suresh Kumar',
        'parent_phone': '+91-9876543210',
        'parent_email': 'suresh.kumar@email.com',
        'socioeconomic_status': 'Medium',
        'parent_education': 'Graduate'
    }
    
    result = StudentService.create_student(test_student)
    if 'error' in result:
        print(f"   ℹ️  {result['error']}")
    else:
        print(f"   ✅ Student created: {result['student_id']} - {result['first_name']} {result['last_name']}")
    
    # Test 2: Get all students
    print("\n2. Getting all students...")
    students = StudentService.get_all_students()
    print(f"   ✅ Found {len(students)} students")
    
    # Test 3: Get students count
    print("\n3. Getting students count...")
    count = StudentService.get_students_count()
    print(f"   ✅ Total active students: {count['count']}")
    
    # Test 4: Search students
    print("\n4. Searching for 'Rajesh'...")
    results = StudentService.search_students('Rajesh')
    print(f"   ✅ Found {len(results)} matching students")
    
    print("\n" + "=" * 60)
