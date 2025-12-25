"""
Input Validation Utilities
"""
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from config.settings import (
    VALID_GENDERS, VALID_SES, VALID_PARENT_EDU, VALID_GRADES
)


def validate_student_data(data):
    """
    Validate student input data
    Returns: (is_valid: bool, error_message: str)
    """
    
    # Required fields
    required_fields = [
        'age', 'gender', 'grade', 'socioeconomic_status', 'parent_education',
        'current_gpa', 'previous_gpa', 'attendance_percentage',
        'failed_subjects', 'assignment_submission_rate', 'disciplinary_incidents'
    ]
    
    # Check for missing fields
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return False, f"Missing required fields: {', '.join(missing_fields)}"
    
    # Validate age
    age = data.get('age')
    if not isinstance(age, (int, float)) or age < 14 or age > 20:
        return False, "Age must be between 14 and 20"
    
    # Validate gender
    if data.get('gender') not in VALID_GENDERS:
        return False, f"Gender must be one of: {', '.join(VALID_GENDERS)}"
    
    # Validate grade
    if data.get('grade') not in VALID_GRADES:
        return False, f"Grade must be one of: {', '.join(map(str, VALID_GRADES))}"
    
    # Validate socioeconomic status
    if data.get('socioeconomic_status') not in VALID_SES:
        return False, f"Socioeconomic status must be one of: {', '.join(VALID_SES)}"
    
    # Validate parent education
    if data.get('parent_education') not in VALID_PARENT_EDU:
        return False, f"Parent education must be one of: {', '.join(VALID_PARENT_EDU)}"
    
    # Validate GPA (0-100)
    current_gpa = data.get('current_gpa')
    if not isinstance(current_gpa, (int, float)) or current_gpa < 0 or current_gpa > 100:
        return False, "Current GPA must be between 0 and 100"
    
    previous_gpa = data.get('previous_gpa')
    if not isinstance(previous_gpa, (int, float)) or previous_gpa < 0 or previous_gpa > 100:
        return False, "Previous GPA must be between 0 and 100"
    
    # Validate attendance (0-100%)
    attendance = data.get('attendance_percentage')
    if not isinstance(attendance, (int, float)) or attendance < 0 or attendance > 100:
        return False, "Attendance percentage must be between 0 and 100"
    
    # Validate failed subjects
    failed = data.get('failed_subjects')
    if not isinstance(failed, (int, float)) or failed < 0 or failed > 10:
        return False, "Failed subjects must be between 0 and 10"
    
    # Validate assignment submission rate
    assignment_rate = data.get('assignment_submission_rate')
    if not isinstance(assignment_rate, (int, float)) or assignment_rate < 0 or assignment_rate > 100:
        return False, "Assignment submission rate must be between 0 and 100"
    
    # Validate disciplinary incidents
    incidents = data.get('disciplinary_incidents')
    if not isinstance(incidents, (int, float)) or incidents < 0 or incidents > 20:
        return False, "Disciplinary incidents must be between 0 and 20"
    
    return True, ""


# Test validation
if __name__ == "__main__":
    # Test valid data
    test_data = {
        'age': 16,
        'gender': 'Male',
        'grade': 10,
        'socioeconomic_status': 'Medium',
        'parent_education': 'Graduate',
        'current_gpa': 75,
        'previous_gpa': 72,
        'attendance_percentage': 85,
        'failed_subjects': 0,
        'assignment_submission_rate': 90,
        'disciplinary_incidents': 0
    }
    
    is_valid, error = validate_student_data(test_data)
    print(f"Validation result: {is_valid}")
    if not is_valid:
        print(f"Error: {error}")
    else:
        print("✓ All validations passed!")
