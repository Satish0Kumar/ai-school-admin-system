-- ============================================
-- SCHOLARSENSE - DATABASE SCHEMA
-- AI-Powered Academic Intelligence System
-- ============================================

-- ============================================
-- TABLE 1: USERS (Admin & Teachers)
-- ============================================
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('admin', 'teacher')),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    CONSTRAINT valid_email CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$')
);

-- ============================================
-- TABLE 2: STUDENTS (Grades 6-10)
-- ============================================
CREATE TABLE IF NOT EXISTS students (
    id SERIAL PRIMARY KEY,
    student_id VARCHAR(50) UNIQUE NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    grade INTEGER NOT NULL CHECK (grade BETWEEN 6 AND 10),
    section VARCHAR(10),
    age INTEGER CHECK (age BETWEEN 10 AND 20),
    gender VARCHAR(10) CHECK (gender IN ('Male', 'Female')),
    date_of_birth DATE,
    parent_name VARCHAR(255),
    parent_phone VARCHAR(20),
    parent_email VARCHAR(255),
    socioeconomic_status VARCHAR(20) CHECK (socioeconomic_status IN ('Low', 'Medium', 'High')),
    parent_education VARCHAR(50) CHECK (parent_education IN ('None', 'High School', 'Graduate', 'Post-Graduate')),
    enrollment_date DATE DEFAULT CURRENT_DATE,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- TABLE 3: ACADEMIC RECORDS
-- ============================================
CREATE TABLE IF NOT EXISTS academic_records (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES students(id) ON DELETE CASCADE,
    semester VARCHAR(20) NOT NULL,
    current_gpa DECIMAL(5,2) CHECK (current_gpa >= 0 AND current_gpa <= 100),
    previous_gpa DECIMAL(5,2) CHECK (previous_gpa >= 0 AND previous_gpa <= 100),
    grade_trend DECIMAL(5,2),
    failed_subjects INTEGER DEFAULT 0 CHECK (failed_subjects >= 0),
    total_subjects INTEGER DEFAULT 5,
    assignment_submission_rate DECIMAL(5,2) CHECK (assignment_submission_rate >= 0 AND assignment_submission_rate <= 100),
    math_score DECIMAL(5,2),
    science_score DECIMAL(5,2),
    english_score DECIMAL(5,2),
    social_score DECIMAL(5,2),
    language_score DECIMAL(5,2),
    recorded_date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(student_id, semester)
);

-- ============================================
-- TABLE 4: ATTENDANCE RECORDS
-- ============================================
CREATE TABLE IF NOT EXISTS attendance (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES students(id) ON DELETE CASCADE,
    attendance_date DATE NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('present', 'absent', 'late', 'excused')),
    period VARCHAR(20) DEFAULT 'all_day',
    arrival_time TIME,
    marked_by INTEGER REFERENCES users(id),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(student_id, attendance_date, period)
);

-- ============================================
-- TABLE 5: BEHAVIORAL INCIDENTS
-- ============================================
CREATE TABLE IF NOT EXISTS behavioral_incidents (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES students(id) ON DELETE CASCADE,
    incident_date DATE NOT NULL,
    incident_time TIME,
    incident_type VARCHAR(50) NOT NULL CHECK (incident_type IN ('Disciplinary', 'Disruptive', 'Bullying', 'Late Arrival', 'Absence', 'Other')),
    severity VARCHAR(20) CHECK (severity IN ('Minor', 'Moderate', 'Serious', 'Critical')),
    description TEXT NOT NULL,
    location VARCHAR(255),
    action_taken TEXT,
    reported_by INTEGER REFERENCES users(id),
    witnesses TEXT,
    parent_notified BOOLEAN DEFAULT false,
    counseling_given BOOLEAN DEFAULT false,
    follow_up_date DATE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- TABLE 6: RISK PREDICTIONS
-- ============================================
CREATE TABLE IF NOT EXISTS risk_predictions (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES students(id) ON DELETE CASCADE,
    prediction_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    risk_level INTEGER NOT NULL CHECK (risk_level BETWEEN 0 AND 3),
    risk_label VARCHAR(20) NOT NULL,
    confidence_score DECIMAL(5,2) NOT NULL CHECK (confidence_score >= 0 AND confidence_score <= 100),
    probability_low DECIMAL(5,2),
    probability_medium DECIMAL(5,2),
    probability_high DECIMAL(5,2),
    probability_critical DECIMAL(5,2),
    features_used JSONB,
    model_version VARCHAR(20) DEFAULT '1.0',
    predicted_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- INDEXES for Performance
-- ============================================
CREATE INDEX IF NOT EXISTS idx_students_grade ON students(grade);
CREATE INDEX IF NOT EXISTS idx_students_active ON students(is_active);
CREATE INDEX IF NOT EXISTS idx_students_student_id ON students(student_id);
CREATE INDEX IF NOT EXISTS idx_attendance_date ON attendance(attendance_date);
CREATE INDEX IF NOT EXISTS idx_attendance_student ON attendance(student_id);
CREATE INDEX IF NOT EXISTS idx_academic_student ON academic_records(student_id);
CREATE INDEX IF NOT EXISTS idx_academic_semester ON academic_records(semester);
CREATE INDEX IF NOT EXISTS idx_behavioral_student ON behavioral_incidents(student_id);
CREATE INDEX IF NOT EXISTS idx_behavioral_date ON behavioral_incidents(incident_date);
CREATE INDEX IF NOT EXISTS idx_predictions_student ON risk_predictions(student_id);
CREATE INDEX IF NOT EXISTS idx_predictions_date ON risk_predictions(prediction_date);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);

-- ============================================
-- TRIGGERS: Auto-update timestamps
-- ============================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_students_updated_at BEFORE UPDATE ON students
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_academic_updated_at BEFORE UPDATE ON academic_records
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- DEFAULT ADMIN USER
-- Password: admin123 (hashed with bcrypt)
-- ============================================
INSERT INTO users (username, email, password_hash, full_name, role, is_active)
VALUES ('admin', 'admin@scholarsense.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYbOcgXy5pK', 'System Administrator', 'admin', true)
ON CONFLICT (email) DO NOTHING;

-- ============================================
-- SUCCESS MESSAGE
-- ============================================
DO $$
BEGIN
    RAISE NOTICE '✅ ScholarSense database schema created successfully!';
    RAISE NOTICE '📊 Tables created: 6';
    RAISE NOTICE '👤 Default admin: admin@scholarsense.com / admin123';
END $$;
