"""
SQLAlchemy ORM Models
ScholarSense - AI-Powered Academic Intelligence System
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Time, Text, DECIMAL, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime, date
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
    __table_args__ = (
        CheckConstraint('grade BETWEEN 6 AND 10', name='valid_grade'),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String(50), unique=True, nullable=False, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    grade = Column(Integer, nullable=False, index=True)
    section = Column(String(10))
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
    marks_entries = relationship("MarksEntry", back_populates="student", cascade="all, delete-orphan")
    communications    = relationship("Communication",     back_populates="student", cascade="all, delete-orphan")
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def computed_age(self) -> int:
        """Compute age from date_of_birth"""
        if self.date_of_birth:
            today = date.today()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None  # No fallback
    
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
            'age': self.computed_age,  # Use computed age from date_of_birth
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



class Attendance(Base):
    __tablename__ = 'attendance'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey('students.id'), nullable=False)
    attendance_date = Column(Date, nullable=False)
    status = Column(String(20), nullable=False)
    remarks = Column(Text)  # ← ADD THIS IF MISSING
    marked_by = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    student = relationship("Student", back_populates="attendance_records")
    marker = relationship("User", foreign_keys=[marked_by])
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'attendance_date': str(self.attendance_date),
            'status': self.status,
            'remarks': self.remarks,  # ← ADD THIS IF MISSING
            'marked_by': self.marked_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
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
# MARKS ENTRY MODEL - Enhancement 6
# ============================================
class MarksEntry(Base):
    """Marks entry records per student per exam"""
    __tablename__ = 'marks_entry'

    id              = Column(Integer, primary_key=True, index=True)
    student_id      = Column(
                        Integer,
                        ForeignKey('students.id', ondelete='CASCADE'),
                        nullable=False,
                        index=True
                      )
    grade           = Column(Integer, nullable=False, index=True)
    section         = Column(String(10))
    semester        = Column(String(20), nullable=False, index=True)
    exam_type       = Column(String(30), nullable=False)
    math_score      = Column(DECIMAL(5, 2))
    science_score   = Column(DECIMAL(5, 2))
    english_score   = Column(DECIMAL(5, 2))
    social_score    = Column(DECIMAL(5, 2))
    language_score  = Column(DECIMAL(5, 2))
    total_marks     = Column(DECIMAL(5, 2))
    gpa             = Column(DECIMAL(5, 2))
    failed_subjects = Column(Integer, default=0)
    assignment_submission_rate = Column(DECIMAL(5, 2), default=100.0)
    entered_by      = Column(Integer, ForeignKey('users.id'))
    entered_at      = Column(DateTime, default=datetime.utcnow)
    updated_at      = Column(DateTime, default=datetime.utcnow,
                             onupdate=datetime.utcnow)
    remarks         = Column(Text)

    # Relationships
    student         = relationship("Student", back_populates="marks_entries")
    enterer         = relationship("User",    foreign_keys=[entered_by])

    def __repr__(self):
        return (
            f"<MarksEntry(student_id={self.student_id}, "
            f"semester='{self.semester}', "
            f"exam='{self.exam_type}', gpa={self.gpa})>"
        )

    def to_dict(self):
        return {
            'id'             : self.id,
            'student_id'     : self.student_id,
            'grade'          : self.grade,
            'section'        : self.section,
            'semester'       : self.semester,
            'exam_type'      : self.exam_type,
            'math_score'     : float(self.math_score)     if self.math_score     else None,
            'science_score'  : float(self.science_score)  if self.science_score  else None,
            'english_score'  : float(self.english_score)  if self.english_score  else None,
            'social_score'   : float(self.social_score)   if self.social_score   else None,
            'language_score' : float(self.language_score) if self.language_score else None,
            'total_marks'    : float(self.total_marks)    if self.total_marks    else None,
            'gpa'            : float(self.gpa)            if self.gpa            else None,
            'failed_subjects': self.failed_subjects,
            'assignment_submission_rate': float(self.assignment_submission_rate)
                               if self.assignment_submission_rate else None,
            'entered_by'     : self.entered_by,
            'entered_at'     : self.entered_at.isoformat() if self.entered_at else None,
            'remarks'        : self.remarks
        }



# ============================================
# COMMUNICATION MODEL - Enhancement 9
# ============================================
class Communication(Base):
    """Parent communication records"""
    __tablename__ = 'communications'

    id                 = Column(Integer, primary_key=True, index=True)
    student_id         = Column(
                           Integer,
                           ForeignKey('students.id', ondelete='CASCADE'),
                           nullable=False,
                           index=True
                         )
    parent_email       = Column(String(255), nullable=False)
    parent_name        = Column(String(255))
    subject            = Column(String(500), nullable=False)
    message_body       = Column(Text, nullable=False)
    template_used      = Column(String(100))
    communication_type = Column(String(50), nullable=False)
    risk_label         = Column(String(20))
    sent_by            = Column(Integer, ForeignKey('users.id'))
    sent_at            = Column(DateTime, default=datetime.utcnow)
    status             = Column(String(20), default='sent')
    sendgrid_id        = Column(String(255))
    error_message      = Column(Text)
    created_at         = Column(DateTime, default=datetime.utcnow)

    # Relationships
    student  = relationship("Student", back_populates="communications")
    sender   = relationship("User",    foreign_keys=[sent_by])

    def __repr__(self):
        return (
            f"<Communication(student_id={self.student_id}, "
            f"type='{self.communication_type}', "
            f"status='{self.status}')>"
        )

    def to_dict(self):
        return {
            'id'                : self.id,
            'student_id'        : self.student_id,
            'parent_email'      : self.parent_email,
            'parent_name'       : self.parent_name,
            'subject'           : self.subject,
            'message_body'      : self.message_body,
            'template_used'     : self.template_used,
            'communication_type': self.communication_type,
            'risk_label'        : self.risk_label,
            'sent_by'           : self.sent_by,
            'sent_at'           : self.sent_at.isoformat()
                                  if self.sent_at else None,
            'status'            : self.status,
            'sendgrid_id'       : self.sendgrid_id,
            'error_message'     : self.error_message,
            'created_at'        : self.created_at.isoformat()
                                  if self.created_at else None
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


# ============================================
# OTP TOKEN MODEL
# ============================================
class OtpToken(Base):
    """OTP tokens for 2FA authentication"""
    __tablename__ = 'otp_tokens'

    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'),
                        nullable=False, index=True)
    otp_code = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    is_used    = Column(Boolean, default=False)
    attempts   = Column(Integer, default=0)

    # Relationship
    user = relationship("User", foreign_keys=[user_id])

    def __repr__(self):
        return (f"<OtpToken(user_id={self.user_id}, "
                f"expires_at='{self.expires_at}', "
                f"is_used={self.is_used})>")

    def to_dict(self):
        return {
            'id'        : self.id,
            'user_id'   : self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'is_used'   : self.is_used,
            'attempts'  : self.attempts
        }



# ============================================
# NOTIFICATION MODEL
# ============================================
class Notification(Base):
    """Parent notification records"""
    __tablename__ = 'notifications'

    id                 = Column(Integer, primary_key=True, index=True)
    student_id         = Column(Integer, ForeignKey('students.id',
                                 ondelete='CASCADE'), nullable=False, index=True)
    notification_type  = Column(String(50), nullable=False)
    trigger_reason     = Column(String(255), nullable=False)
    message            = Column(Text, nullable=False)
    sent_to_email      = Column(String(255), nullable=False)
    sent_to_name       = Column(String(255))
    status             = Column(String(20), default='pending')
    sent_at            = Column(DateTime)
    created_at         = Column(DateTime, default=datetime.utcnow)
    academic_record_id = Column(Integer, ForeignKey('academic_records.id',
                                 ondelete='SET NULL'), nullable=True)
    prediction_id      = Column(Integer, ForeignKey('risk_predictions.id',
                                 ondelete='SET NULL'), nullable=True)
    error_message      = Column(Text, nullable=True)

    # Relationships
    student        = relationship("Student",        foreign_keys=[student_id])
    academic_record= relationship("AcademicRecord", foreign_keys=[academic_record_id])
    prediction     = relationship("RiskPrediction", foreign_keys=[prediction_id])

    def __repr__(self):
        return (f"<Notification(student_id={self.student_id}, "
                f"type='{self.notification_type}', "
                f"status='{self.status}')>")

    def to_dict(self):
        return {
            'id'               : self.id,
            'student_id'       : self.student_id,
            'notification_type': self.notification_type,
            'trigger_reason'   : self.trigger_reason,
            'message'          : self.message,
            'sent_to_email'    : self.sent_to_email,
            'sent_to_name'     : self.sent_to_name,
            'status'           : self.status,
            'sent_at'          : self.sent_at.isoformat() if self.sent_at else None,
            'created_at'       : self.created_at.isoformat() if self.created_at else None,
            'academic_record_id': self.academic_record_id,
            'prediction_id'    : self.prediction_id,
            'error_message'    : self.error_message
        }
