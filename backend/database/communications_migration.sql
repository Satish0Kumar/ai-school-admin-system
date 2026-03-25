-- ============================================
-- COMMUNICATIONS TABLE - Enhancement 9
-- ScholarSense - AI-Powered Academic Intelligence System
-- ============================================

CREATE TABLE IF NOT EXISTS communications (
    id              SERIAL PRIMARY KEY,
    student_id      INTEGER REFERENCES students(id) ON DELETE CASCADE,
    parent_email    VARCHAR(255) NOT NULL,
    parent_name     VARCHAR(255),
    subject         VARCHAR(500) NOT NULL,
    message_body    TEXT NOT NULL,
    template_used   VARCHAR(100),
    communication_type VARCHAR(50) NOT NULL
                    CHECK (communication_type IN (
                        'Risk Alert', 'Academic Warning',
                        'Behavioral Notice', 'General Update',
                        'Attendance Alert', 'Marks Report',
                        'Custom'
                    )),
    risk_label      VARCHAR(20),
    sent_by         INTEGER REFERENCES users(id),
    sent_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status          VARCHAR(20) DEFAULT 'sent'
                    CHECK (status IN ('sent', 'failed', 'pending')),
    sendgrid_id     VARCHAR(255),
    error_message   TEXT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_comm_student    ON communications(student_id);
CREATE INDEX IF NOT EXISTS idx_comm_sent_by    ON communications(sent_by);
CREATE INDEX IF NOT EXISTS idx_comm_type       ON communications(communication_type);
CREATE INDEX IF NOT EXISTS idx_comm_status     ON communications(status);
CREATE INDEX IF NOT EXISTS idx_comm_sent_at    ON communications(sent_at);

DO $$
BEGIN
    RAISE NOTICE '✅ communications table created successfully!';
END $$;
