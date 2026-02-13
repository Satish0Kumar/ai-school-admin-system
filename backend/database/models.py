"""
SQLAlchemy ORM Models
ScholarSense - AI-Powered Academic Intelligence System
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Time, Text, DECIMAL, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database.db_config import Base

# ============================================
# USER MODEL
# ============================================
class User(Base):
    """Admin and Teacher users"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)  # 'admin' or 'teacher'
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    
    # Relationships
    attendances_marked = relationship("Attendance", back_populates="marker")
    incidents_reported = relationship("BehavioralIncident", back_populates="reporter")
    predictions_made = relationship("RiskPrediction", back_populates="predictor")
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

# ============================================
# STUDENT MODEL
# ============================================
class Student(Base):
    """Student records for grades 6-10"""
    __tablename__ = 'students'
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String(50), unique=True, nullable=False, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    grade = Column(Integer, nullable=False, index=True)
    section = Column(String(10))
    age = Column(Integer)
    gender = Column(String(10))
    date_of_birth = Column(Date)
    parent_name = Column(String(255))
    parent_phone = Column(String(20))
    parent_email = Column(String(255))
    socioeconomic_status = Column(String(20))
    parent_education = Column(String(50))
    enrollment_date = Column(Date, default=datetime.utcnow().date())
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    academic_records = relationship("AcademicRecord", back_populates="student", cascade="all, delete-orphan")
    attendance_records = relationship("Attendance", back_populates="student", cascade="all, delete-orphan")
    incidents = relationship("BehavioralIncident", back_populates="student", cascade="all, delete-orphan")
    predictions = relationship("RiskPrediction", back_populates="student", cascade="all, delete-orphan")
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def __repr__(self):
        return f"<Student(id={self.id}, student_id='{self.student_id}', name='{self.full_name}')>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'student_id': self.student_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'grade': self.grade,
            'section': self.section,
            'age': self.age,
            'gender': self.gender,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'parent_name': self.parent_name,
            'parent_phone': self.parent_phone,
            'parent_email': self.parent_email,
            'socioeconomic_status': self.socioeconomic_status,
            'parent_education': self.parent_education,
            'enrollment_date': self.enrollment_date.isoformat() if self.enrollment_date else None,
            'is_active': self.is_active
        }

# ============================================
# ACADEMIC RECORD MODEL
# ============================================
class AcademicRecord(Base):
    """Academic performance records"""
    __tablename__ = 'academic_records'
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey('students.id', ondelete='CASCADE'), nullable=False, index=True)
    semester = Column(String(20), nullable=False, index=True)
    current_gpa = Column(DECIMAL(5, 2))
    previous_gpa = Column(DECIMAL(5, 2))
    grade_trend = Column(DECIMAL(5, 2))
    failed_subjects = Column(Integer, default=0)
    total_subjects = Column(Integer, default=5)
    assignment_submission_rate = Column(DECIMAL(5, 2))
    math_score = Column(DECIMAL(5, 2))
    science_score = Column(DECIMAL(5, 2))
    english_score = Column(DECIMAL(5, 2))
    social_score = Column(DECIMAL(5, 2))
    language_score = Column(DECIMAL(5, 2))
    recorded_date = Column(Date, default=datetime.utcnow().date())
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    student = relationship("Student", back_populates="academic_records")
    
    def __repr__(self):
        return f"<AcademicRecord(student_id={self.student_id}, semester='{self.semester}', gpa={self.current_gpa})>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'student_id': self.student_id,
            'semester': self.semester,
            'current_gpa': float(self.current_gpa) if self.current_gpa else None,
            'previous_gpa': float(self.previous_gpa) if self.previous_gpa else None,
            'grade_trend': float(self.grade_trend) if self.grade_trend else None,
            'failed_subjects': self.failed_subjects,
            'total_subjects': self.total_subjects,
            'assignment_submission_rate': float(self.assignment_submission_rate) if self.assignment_submission_rate else None,
            'math_score': float(self.math_score) if self.math_score else None,
            'science_score': float(self.science_score) if self.science_score else None,
            'english_score': float(self.english_score) if self.english_score else None,
            'social_score': float(self.social_score) if self.social_score else None,
            'language_score': float(self.language_score) if self.language_score else None,
            'recorded_date': self.recorded_date.isoformat() if self.recorded_date else None
        }

# ============================================
# ATTENDANCE MODEL
# ============================================
class Attendance(Base):
    """Daily attendance records"""
    __tablename__ = 'attendance'
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey('students.id', ondelete='CASCADE'), nullable=False, index=True)
    attendance_date = Column(Date, nullable=False, index=True)
    status = Column(String(20), nullable=False)  # present, absent, late, excused
    period = Column(String(20), default='all_day')
    arrival_time = Column(Time)
    marked_by = Column(Integer, ForeignKey('users.id'))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    student = relationship("Student", back_populates="attendance_records")
    marker = relationship("User", back_populates="attendances_marked")
    
    def __repr__(self):
        return f"<Attendance(student_id={self.student_id}, date={self.attendance_date}, status='{self.status}')>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'student_id': self.student_id,
            'attendance_date': self.attendance_date.isoformat() if self.attendance_date else None,
            'status': self.status,
            'period': self.period,
            'arrival_time': self.arrival_time.isoformat() if self.arrival_time else None,
            'marked_by': self.marked_by,
            'notes': self.notes
        }

# ============================================
# BEHAVIORAL INCIDENT MODEL
# ============================================
class BehavioralIncident(Base):
    """Behavioral incident records"""
    __tablename__ = 'behavioral_incidents'
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey('students.id', ondelete='CASCADE'), nullable=False, index=True)
    incident_date = Column(Date, nullable=False, index=True)
    incident_time = Column(Time)
    incident_type = Column(String(50), nullable=False)
    severity = Column(String(20))
    description = Column(Text, nullable=False)
    location = Column(String(255))
    action_taken = Column(Text)
    reported_by = Column(Integer, ForeignKey('users.id'))
    witnesses = Column(Text)
    parent_notified = Column(Boolean, default=False)
    counseling_given = Column(Boolean, default=False)
    follow_up_date = Column(Date)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    student = relationship("Student", back_populates="incidents")
    reporter = relationship("User", back_populates="incidents_reported")
    
    def __repr__(self):
        return f"<BehavioralIncident(student_id={self.student_id}, type='{self.incident_type}', severity='{self.severity}')>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'student_id': self.student_id,
            'incident_date': self.incident_date.isoformat() if self.incident_date else None,
            'incident_time': self.incident_time.isoformat() if self.incident_time else None,
            'incident_type': self.incident_type,
            'severity': self.severity,
            'description': self.description,
            'location': self.location,
            'action_taken': self.action_taken,
            'parent_notified': self.parent_notified,
            'counseling_given': self.counseling_given,
            'follow_up_date': self.follow_up_date.isoformat() if self.follow_up_date else None
        }

# ============================================
# RISK PREDICTION MODEL
# ============================================
class RiskPrediction(Base):
    """AI risk prediction records"""
    __tablename__ = 'risk_predictions'
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey('students.id', ondelete='CASCADE'), nullable=False, index=True)
    prediction_date = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    risk_level = Column(Integer, nullable=False)  # 0=Low, 1=Medium, 2=High, 3=Critical
    risk_label = Column(String(20), nullable=False)
    confidence_score = Column(DECIMAL(5, 2), nullable=False)
    probability_low = Column(DECIMAL(5, 2))
    probability_medium = Column(DECIMAL(5, 2))
    probability_high = Column(DECIMAL(5, 2))
    probability_critical = Column(DECIMAL(5, 2))
    features_used = Column(JSONB)
    model_version = Column(String(20), default='1.0')
    predicted_by = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    student = relationship("Student", back_populates="predictions")
    predictor = relationship("User", back_populates="predictions_made")
    
    def __repr__(self):
        return f"<RiskPrediction(student_id={self.student_id}, risk='{self.risk_label}', confidence={self.confidence_score}%)>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'student_id': self.student_id,
            'prediction_date': self.prediction_date.isoformat() if self.prediction_date else None,
            'risk_level': self.risk_level,
            'risk_label': self.risk_label,
            'confidence_score': float(self.confidence_score) if self.confidence_score else None,
            'probability_low': float(self.probability_low) if self.probability_low else None,
            'probability_medium': float(self.probability_medium) if self.probability_medium else None,
            'probability_high': float(self.probability_high) if self.probability_high else None,
            'probability_critical': float(self.probability_critical) if self.probability_critical else None,
            'model_version': self.model_version
        }
