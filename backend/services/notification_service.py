"""
Notification Service - Parent Alert System
ScholarSense - AI-Powered Academic Intelligence System

Trigger Conditions:
  📉 low_gpa        → current_gpa < 50
  🚨 high_risk      → risk_level = High or Critical
  📅 low_attendance → attendance_rate < 75%
  📝 failed_subjects→ failed_subjects >= 2

Auto-triggered when:
  - Academic record is created/updated
  - ML risk prediction is made
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

from backend.database.db_config import SessionLocal
from backend.database.models import (
    Student, AcademicRecord, Attendance,
    RiskPrediction, Notification
)
from backend.services.email_service import EmailService
from sqlalchemy import func

# ── Thresholds ─────────────────────────────────────────────────────────────────
GPA_THRESHOLD         = 50.0    # Below this → low_gpa alert
ATTENDANCE_THRESHOLD  = 75.0    # Below this → low_attendance alert
FAILED_SUBJ_THRESHOLD = 2       # >= this    → failed_subjects alert
HIGH_RISK_LEVELS      = ['High', 'Critical']

# ── Cooldown: Don't spam same alert within N days ──────────────────────────────
COOLDOWN_DAYS = {
    'low_gpa'        : 7,
    'high_risk'      : 3,
    'low_attendance' : 7,
    'failed_subjects': 14
}


class NotificationService:
    """
    Central service for triggering and sending parent notifications.
    All trigger methods return a result dict.
    """

    # ──────────────────────────────────────────────────────────────────────────
    @staticmethod
    def _is_in_cooldown(db, student_id: int, notification_type: str) -> bool:
        """
        Check if a notification of this type was already sent recently.
        Prevents spamming parents with the same alert.
        """
        cooldown_days = COOLDOWN_DAYS.get(notification_type, 7)
        cutoff        = datetime.utcnow() - timedelta(days=cooldown_days)

        recent = db.query(Notification).filter(
            Notification.student_id        == student_id,
            Notification.notification_type == notification_type,
            Notification.status            == 'sent',
            Notification.sent_at           >= cutoff
        ).first()

        return recent is not None

    # ──────────────────────────────────────────────────────────────────────────
    @staticmethod
    def _get_attendance_rate(db, student_id: int, days: int = 30) -> float:
        """Get attendance rate for student over last N days"""
        cutoff = datetime.utcnow() - timedelta(days=days)

        total = db.query(func.count(Attendance.id)).filter(
            Attendance.student_id    == student_id,
            Attendance.attendance_date >= cutoff.date()
        ).scalar() or 0

        if total == 0:
            return 100.0

        present = db.query(func.count(Attendance.id)).filter(
            Attendance.student_id    == student_id,
            Attendance.attendance_date >= cutoff.date(),
            Attendance.status        == 'present'
        ).scalar() or 0

        return round((present / total) * 100, 2)

    # ──────────────────────────────────────────────────────────────────────────
    @staticmethod
    def _create_notification_record(
        db,
        student           : Student,
        notification_type : str,
        trigger_reason    : str,
        message           : str,
        academic_record_id: int = None,
        prediction_id     : int = None
    ) -> Notification:
        """
        Save notification record to DB before sending email.
        Returns the saved Notification object.
        """
        notification = Notification(
            student_id         = student.id,
            notification_type  = notification_type,
            trigger_reason     = trigger_reason,
            message            = message,
            sent_to_email      = student.parent_email,
            sent_to_name       = student.parent_name,
            status             = 'pending',
            created_at         = datetime.utcnow(),
            academic_record_id = academic_record_id,
            prediction_id      = prediction_id
        )
        db.add(notification)
        db.flush()
        return notification

    # ──────────────────────────────────────────────────────────────────────────
    @staticmethod
    def _send_and_update(
        db,
        notification      : Notification,
        student           : Student,
        notification_type : str,
        trigger_reason    : str,
        details           : dict
    ) -> dict:
        """
        Send email and update notification status in DB.
        Returns result dict.
        """
        try:
            email_result = EmailService.send_parent_notification(
                to_email         = student.parent_email,
                parent_name      = student.parent_name or "Parent/Guardian",
                student_name     = f"{student.first_name} {student.last_name}",
                student_grade    = student.grade,
                student_section  = student.section,
                notification_type= notification_type,
                trigger_reason   = trigger_reason,
                details          = details
            )

            if email_result['status'] == 'sent':
                notification.status  = 'sent'
                notification.sent_at = datetime.utcnow()
                notification.message = trigger_reason
                db.commit()

                print(f"✅ Notification sent: {notification_type} → "
                      f"{student.first_name} {student.last_name} "
                      f"→ {student.parent_email}")

                return {
                    'status'           : 'sent',
                    'notification_id'  : notification.id,
                    'notification_type': notification_type,
                    'sent_to'          : student.parent_email,
                    'student'          : f"{student.first_name} {student.last_name}"
                }
            else:
                notification.status        = 'failed'
                notification.error_message = email_result['message']
                db.commit()

                print(f"❌ Notification failed: {notification_type} → "
                      f"{student.first_name} {student.last_name}: "
                      f"{email_result['message']}")

                return {
                    'status' : 'failed',
                    'message': email_result['message']
                }

        except Exception as e:
            notification.status        = 'failed'
            notification.error_message = str(e)
            db.commit()
            print(f"❌ Notification exception: {e}")
            return {'status': 'failed', 'message': str(e)}

    # ══════════════════════════════════════════════════════════════════════════
    # PUBLIC TRIGGER METHODS
    # ══════════════════════════════════════════════════════════════════════════

    @staticmethod
    def check_and_notify_academic(
        student_id        : int,
        academic_record_id: int = None
    ) -> list:
        """
        Check academic record and send relevant notifications.
        Called automatically when academic record is created/updated.

        Returns list of notification results.
        """
        db      = SessionLocal()
        results = []

        try:
            # ── Get student ─────────────────────────────────────────────────
            student = db.query(Student).filter(
                Student.id == student_id
            ).first()

            if not student:
                return [{'status': 'failed', 'message': 'Student not found'}]

            if not student.parent_email:
                print(f"⚠️  No parent email for student {student_id}")
                return [{'status': 'skipped', 'message': 'No parent email'}]

            # ── Get latest academic record ───────────────────────────────────
            academic = db.query(AcademicRecord).filter(
                AcademicRecord.student_id == student_id
            ).order_by(AcademicRecord.recorded_date.desc()).first()

            if not academic:
                return [{'status': 'skipped', 'message': 'No academic record'}]

            student_name = f"{student.first_name} {student.last_name}"

            # ── CHECK 1: Low GPA ────────────────────────────────────────────
            if float(academic.current_gpa or 0) < GPA_THRESHOLD:
                if not NotificationService._is_in_cooldown(
                    db, student_id, 'low_gpa'
                ):
                    reason = (
                        f"{student_name}'s current GPA has dropped to "
                        f"{academic.current_gpa:.1f}% which is below the "
                        f"required threshold of {GPA_THRESHOLD}%."
                    )
                    details = {
                        'Current GPA'  : f"{academic.current_gpa:.1f}%",
                        'Previous GPA' : f"{academic.previous_gpa:.1f}%",
                        'Grade Trend'  : (
                            f"{'📈' if academic.grade_trend >= 0 else '📉'} "
                            f"{academic.grade_trend:+.1f}%"
                        ),
                        'Math Score'   : f"{academic.math_score:.1f}%",
                        'Science Score': f"{academic.science_score:.1f}%",
                        'English Score': f"{academic.english_score:.1f}%",
                    }
                    notif = NotificationService._create_notification_record(
                        db, student, 'low_gpa', reason, reason,
                        academic_record_id=academic.id
                    )
                    result = NotificationService._send_and_update(
                        db, notif, student, 'low_gpa', reason, details
                    )
                    results.append(result)
                else:
                    print(f"⏳ low_gpa cooldown active for {student_name}")

            # ── CHECK 2: Failed Subjects ─────────────────────────────────────
            failed = int(academic.failed_subjects or 0)
            if failed >= FAILED_SUBJ_THRESHOLD:
                if not NotificationService._is_in_cooldown(
                    db, student_id, 'failed_subjects'
                ):
                    reason = (
                        f"{student_name} has failed {failed} subject(s) "
                        f"this semester. Immediate attention is required."
                    )
                    # Find which subjects failed
                    failed_list = []
                    subject_scores = {
                        'Math'    : academic.math_score,
                        'Science' : academic.science_score,
                        'English' : academic.english_score,
                        'Social'  : academic.social_score,
                        'Language': academic.language_score,
                    }
                    for subj, score in subject_scores.items():
                        if score is not None and float(score) < 35:
                            failed_list.append(f"{subj} ({score:.1f}%)")

                    details = {
                        'Failed Subjects' : ', '.join(failed_list) or f"{failed} subjects",
                        'Total Subjects'  : str(academic.total_subjects or 5),
                        'Current GPA'     : f"{academic.current_gpa:.1f}%",
                        'Submission Rate' : f"{academic.assignment_submission_rate:.1f}%",
                    }
                    notif = NotificationService._create_notification_record(
                        db, student, 'failed_subjects', reason, reason,
                        academic_record_id=academic.id
                    )
                    result = NotificationService._send_and_update(
                        db, notif, student, 'failed_subjects', reason, details
                    )
                    results.append(result)
                else:
                    print(f"⏳ failed_subjects cooldown active for {student_name}")

            # ── CHECK 3: Low Attendance ──────────────────────────────────────
            attendance_rate = NotificationService._get_attendance_rate(
                db, student_id, days=30
            )
            if attendance_rate < ATTENDANCE_THRESHOLD:
                if not NotificationService._is_in_cooldown(
                    db, student_id, 'low_attendance'
                ):
                    reason = (
                        f"{student_name}'s attendance has dropped to "
                        f"{attendance_rate:.1f}% in the last 30 days, "
                        f"which is below the required {ATTENDANCE_THRESHOLD}%."
                    )
                    details = {
                        'Attendance Rate' : f"{attendance_rate:.1f}%",
                        'Required Rate'   : f"{ATTENDANCE_THRESHOLD}%",
                        'Period'          : 'Last 30 days',
                        'Status'          : '⚠️ Below minimum requirement'
                    }
                    notif = NotificationService._create_notification_record(
                        db, student, 'low_attendance', reason, reason,
                        academic_record_id=academic.id
                    )
                    result = NotificationService._send_and_update(
                        db, notif, student, 'low_attendance', reason, details
                    )
                    results.append(result)
                else:
                    print(f"⏳ low_attendance cooldown active for {student_name}")

            if not results:
                results.append({
                    'status' : 'no_trigger',
                    'message': 'No notification conditions met'
                })

            return results

        except Exception as e:
            db.rollback()
            print(f"❌ check_and_notify_academic error: {e}")
            return [{'status': 'failed', 'message': str(e)}]
        finally:
            db.close()

    # ──────────────────────────────────────────────────────────────────────────
    @staticmethod
    def check_and_notify_risk(
        student_id   : int,
        prediction_id: int,
        risk_label   : str
    ) -> dict:
        """
        Check ML prediction result and send high_risk notification.
        Called automatically after risk prediction is made.

        Args:
            student_id   : Student DB id
            prediction_id: RiskPrediction DB id
            risk_label   : 'Low' | 'Medium' | 'High' | 'Critical'

        Returns: notification result dict
        """
        if risk_label not in HIGH_RISK_LEVELS:
            return {
                'status' : 'no_trigger',
                'message': f'Risk level {risk_label} does not require notification'
            }

        db = SessionLocal()
        try:
            student = db.query(Student).filter(
                Student.id == student_id
            ).first()

            if not student or not student.parent_email:
                return {'status': 'skipped', 'message': 'No parent email'}

            if NotificationService._is_in_cooldown(db, student_id, 'high_risk'):
                student_name = f"{student.first_name} {student.last_name}"
                print(f"⏳ high_risk cooldown active for {student_name}")
                return {'status': 'cooldown', 'message': 'Notification cooldown active'}

            student_name = f"{student.first_name} {student.last_name}"

            # ── Get prediction details ───────────────────────────────────────
            prediction = db.query(RiskPrediction).filter(
                RiskPrediction.id == prediction_id
            ).first()

            risk_emoji = '🔴' if risk_label == 'Critical' else '🟠'
            reason = (
                f"{student_name} has been identified as {risk_emoji} "
                f"{risk_label} Risk by our AI academic monitoring system. "
                f"Immediate intervention is recommended."
            )

            details = {
                'Risk Level'      : f"{risk_emoji} {risk_label}",
                'Confidence'      : f"{float(prediction.confidence_score):.1f}%" if prediction else 'N/A',
                'Assessment Date' : datetime.utcnow().strftime('%d %b %Y'),
                'Recommendation'  : 'Schedule parent-teacher meeting'
            }

            notif = NotificationService._create_notification_record(
                db, student, 'high_risk', reason, reason,
                prediction_id=prediction_id
            )
            return NotificationService._send_and_update(
                db, notif, student, 'high_risk', reason, details
            )

        except Exception as e:
            db.rollback()
            print(f"❌ check_and_notify_risk error: {e}")
            return {'status': 'failed', 'message': str(e)}
        finally:
            db.close()

    # ──────────────────────────────────────────────────────────────────────────
    @staticmethod
    def send_manual_notification(
        student_id       : int,
        notification_type: str,
        custom_message   : str
    ) -> dict:
        """
        Manually send a notification from the frontend.
        Used by teachers/admins to send custom alerts.

        Args:
            student_id       : Student DB id
            notification_type: Alert type key
            custom_message   : Custom message to send

        Returns: notification result dict
        """
        db = SessionLocal()
        try:
            student = db.query(Student).filter(
                Student.id == student_id
            ).first()

            if not student:
                return {'status': 'failed', 'message': 'Student not found'}

            if not student.parent_email:
                return {'status': 'failed', 'message': 'No parent email configured'}

            student_name = f"{student.first_name} {student.last_name}"

            details = {
                'Message Type': 'Manual Notification',
                'Sent By'     : 'School Administration',
                'Date'        : datetime.utcnow().strftime('%d %b %Y %H:%M')
            }

            notif = NotificationService._create_notification_record(
                db, student, notification_type,
                custom_message, custom_message
            )
            return NotificationService._send_and_update(
                db, notif, student, notification_type, custom_message, details
            )

        except Exception as e:
            db.rollback()
            print(f"❌ Manual notification error: {e}")
            return {'status': 'failed', 'message': str(e)}
        finally:
            db.close()

    # ──────────────────────────────────────────────────────────────────────────
    @staticmethod
    def get_notification_stats() -> dict:
        """
        Get notification statistics for dashboard.
        Returns counts by status and type.
        """
        db = SessionLocal()
        try:
            total = db.query(func.count(Notification.id)).scalar() or 0
            sent  = db.query(func.count(Notification.id)).filter(
                Notification.status == 'sent'
            ).scalar() or 0
            failed = db.query(func.count(Notification.id)).filter(
                Notification.status == 'failed'
            ).scalar() or 0
            today  = db.query(func.count(Notification.id)).filter(
                Notification.sent_at >= datetime.utcnow().date()
            ).scalar() or 0

            # Count by type
            type_counts = {}
            for ntype in ['low_gpa','high_risk','low_attendance','failed_subjects']:
                count = db.query(func.count(Notification.id)).filter(
                    Notification.notification_type == ntype,
                    Notification.status == 'sent'
                ).scalar() or 0
                type_counts[ntype] = count

            return {
                'total'      : total,
                'sent'       : sent,
                'failed'     : failed,
                'today'      : today,
                'by_type'    : type_counts
            }

        except Exception as e:
            print(f"❌ Stats error: {e}")
            return {'total':0,'sent':0,'failed':0,'today':0,'by_type':{}}
        finally:
            db.close()

    # ──────────────────────────────────────────────────────────────────────────
    @staticmethod
    def get_student_notifications(student_id: int, limit: int = 20) -> list:
        """Get notification history for a specific student"""
        db = SessionLocal()
        try:
            notifications = db.query(Notification).filter(
                Notification.student_id == student_id
            ).order_by(
                Notification.created_at.desc()
            ).limit(limit).all()

            return [n.to_dict() for n in notifications]

        except Exception as e:
            print(f"❌ Get notifications error: {e}")
            return []
        finally:
            db.close()

    # ──────────────────────────────────────────────────────────────────────────
    @staticmethod
    def get_recent_notifications(limit: int = 50) -> list:
        """Get recent notifications across all students"""
        db = SessionLocal()
        try:
            notifications = db.query(Notification).order_by(
                Notification.created_at.desc()
            ).limit(limit).all()

            results = []
            for n in notifications:
                n_dict = n.to_dict()
                # Add student name
                student = db.query(Student).filter(
                    Student.id == n.student_id
                ).first()
                if student:
                    n_dict['student_name'] = (
                        f"{student.first_name} {student.last_name}"
                    )
                    n_dict['grade']   = student.grade
                    n_dict['section'] = student.section
                results.append(n_dict)

            return results

        except Exception as e:
            print(f"❌ Recent notifications error: {e}")
            return []
        finally:
            db.close()
