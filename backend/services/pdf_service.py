"""
PDF Report Generation Service
ScholarSense - AI-Powered Academic Intelligence System

Generates 3 types of PDF reports:
  1. Individual Student Report
  2. Grade/Class Wise Report
  3. At-Risk Students Report

Uses ReportLab library.
"""

import sys
from pathlib import Path
from datetime import datetime, date, timedelta
from io import BytesIO

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# ReportLab imports
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table,
    TableStyle, HRFlowable
)

# Project imports
from backend.database.db_config import SessionLocal
from backend.database.models import (
    Student, AcademicRecord, Attendance,
    RiskPrediction, Notification
)
from backend.config.settings import SCHOOL_NAME, ACADEMIC_YEAR
from sqlalchemy import func

# ── Colors ─────────────────────────────────────────────────────────────────────
PRIMARY    = colors.HexColor('#2563eb')
SECONDARY  = colors.HexColor('#1e40af')
SUCCESS    = colors.HexColor('#10b981')
WARNING    = colors.HexColor('#f59e0b')
DANGER     = colors.HexColor('#ef4444')
PURPLE     = colors.HexColor('#8b5cf6')
LIGHT_BLUE = colors.HexColor('#eff6ff')
LIGHT_GRAY = colors.HexColor('#f9fafb')
MED_GRAY   = colors.HexColor('#e5e7eb')
DARK_GRAY  = colors.HexColor('#374151')
TEXT_GRAY  = colors.HexColor('#6b7280')
WHITE      = colors.white
BLACK      = colors.HexColor('#111827')


# ── Risk colors ────────────────────────────────────────────────────────────────
RISK_COLORS = {
    'Low'     : SUCCESS,
    'Medium'  : WARNING,
    'High'    : colors.HexColor('#f97316'),
    'Critical': DANGER
}

RISK_BG_COLORS = {
    'Low'     : colors.HexColor('#d1fae5'),
    'Medium'  : colors.HexColor('#fef3c7'),
    'High'    : colors.HexColor('#ffedd5'),
    'Critical': colors.HexColor('#fee2e2')
}


class PDFService:
    """Generate PDF reports for ScholarSense"""

    # ──────────────────────────────────────────────────────────────────────────
    @staticmethod
    def _get_styles():
        """Get custom paragraph styles"""
        styles = getSampleStyleSheet()

        custom = {
            'title': ParagraphStyle(
                'CustomTitle',
                parent    = styles['Normal'],
                fontSize  = 24,
                fontName  = 'Helvetica-Bold',
                textColor = WHITE,
                alignment = TA_CENTER,
                spaceAfter= 4
            ),
            'subtitle': ParagraphStyle(
                'CustomSubtitle',
                parent    = styles['Normal'],
                fontSize  = 11,
                fontName  = 'Helvetica',
                textColor = colors.HexColor('#bfdbfe'),
                alignment = TA_CENTER,
                spaceAfter= 2
            ),
            'section': ParagraphStyle(
                'SectionHeader',
                parent    = styles['Normal'],
                fontSize  = 13,
                fontName  = 'Helvetica-Bold',
                textColor = PRIMARY,
                spaceBefore=14,
                spaceAfter= 6
            ),
            'body': ParagraphStyle(
                'BodyText',
                parent    = styles['Normal'],
                fontSize  = 10,
                fontName  = 'Helvetica',
                textColor = DARK_GRAY,
                spaceAfter= 4,
                leading   = 14
            ),
            'small': ParagraphStyle(
                'SmallText',
                parent    = styles['Normal'],
                fontSize  = 8,
                fontName  = 'Helvetica',
                textColor = TEXT_GRAY,
            ),
            'bold': ParagraphStyle(
                'BoldText',
                parent    = styles['Normal'],
                fontSize  = 10,
                fontName  = 'Helvetica-Bold',
                textColor = BLACK,
            ),
            'center': ParagraphStyle(
                'CenterText',
                parent    = styles['Normal'],
                fontSize  = 10,
                fontName  = 'Helvetica',
                textColor = DARK_GRAY,
                alignment = TA_CENTER,
            ),
            'right': ParagraphStyle(
                'RightText',
                parent    = styles['Normal'],
                fontSize  = 9,
                fontName  = 'Helvetica',
                textColor = TEXT_GRAY,
                alignment = TA_RIGHT,
            ),
        }
        return custom

    # ──────────────────────────────────────────────────────────────────────────
    @staticmethod
    def _build_header(styles, title, subtitle=''):
        """Build the header banner for all PDF types"""
        elements = []

        # ── Header background table ─────────────────────────────────────────
        header_data = [[
            Paragraph('🎓 ScholarSense', styles['title']),
        ]]
        if subtitle:
            header_data.append([
                Paragraph(subtitle, styles['subtitle'])
            ])
        header_data.append([
            Paragraph(title, ParagraphStyle(
                'ReportTitle',
                fontSize  = 16,
                fontName  = 'Helvetica-Bold',
                textColor = WHITE,
                alignment = TA_CENTER,
                spaceBefore=6
            ))
        ])
        header_data.append([
            Paragraph(
                f"Generated on: {datetime.utcnow().strftime('%d %B %Y, %I:%M %p')} UTC",
                ParagraphStyle(
                    'GenDate',
                    fontSize  = 9,
                    fontName  = 'Helvetica',
                    textColor = colors.HexColor('#93c5fd'),
                    alignment = TA_CENTER,
                    spaceBefore=4
                )
            )
        ])

        header_table = Table(header_data, colWidths=[17*cm])
        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), PRIMARY),
            ('ALIGN',      (0,0), (-1,-1), 'CENTER'),
            ('VALIGN',     (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 16),
            ('BOTTOMPADDING', (0,-1), (-1,-1), 16),
            ('ROUNDEDCORNERS', [8]),
        ]))

        elements.append(header_table)
        elements.append(Spacer(1, 0.4*cm))
        return elements

    # ──────────────────────────────────────────────────────────────────────────
    @staticmethod
    def _build_info_row(label, value, styles):
        """Build a label-value info row"""
        return Table(
            [[
                Paragraph(f"<b>{label}</b>", styles['body']),
                Paragraph(str(value), styles['body'])
            ]],
            colWidths=[5*cm, 12*cm]
        )

    # ──────────────────────────────────────────────────────────────────────────
    @staticmethod
    def _get_attendance_stats(db, student_id, days=90):
        """Get attendance stats for a student"""
        cutoff = date.today() - timedelta(days=days)

        total = db.query(func.count(Attendance.id)).filter(
            Attendance.student_id      == student_id,
            Attendance.attendance_date >= cutoff
        ).scalar() or 0

        present = db.query(func.count(Attendance.id)).filter(
            Attendance.student_id      == student_id,
            Attendance.attendance_date >= cutoff,
            Attendance.status          == 'present'
        ).scalar() or 0

        absent = db.query(func.count(Attendance.id)).filter(
            Attendance.student_id      == student_id,
            Attendance.attendance_date >= cutoff,
            Attendance.status          == 'absent'
        ).scalar() or 0

        rate = round((present / total * 100), 1) if total > 0 else 0.0
        return {
            'total'  : total,
            'present': present,
            'absent' : absent,
            'rate'   : rate
        }

    # ══════════════════════════════════════════════════════════════════════════
    # REPORT 1 — INDIVIDUAL STUDENT REPORT
    # ══════════════════════════════════════════════════════════════════════════

    @staticmethod
    def generate_student_report(student_id: int) -> bytes:
        """
        Generate individual student PDF report.
        Returns: PDF as bytes
        """
        db = SessionLocal()
        try:
            # ── Fetch data ──────────────────────────────────────────────────
            student = db.query(Student).filter(
                Student.id == student_id
            ).first()

            if not student:
                raise ValueError(f"Student {student_id} not found")

            academic = db.query(AcademicRecord).filter(
                AcademicRecord.student_id == student_id
            ).order_by(AcademicRecord.recorded_date.desc()).first()

            prediction = db.query(RiskPrediction).filter(
                RiskPrediction.student_id == student_id
            ).order_by(RiskPrediction.created_at.desc()).first()

            att_stats = PDFService._get_attendance_stats(db, student_id)

            # ── Build PDF ───────────────────────────────────────────────────
            buffer = BytesIO()
            doc    = SimpleDocTemplate(
                buffer,
                pagesize     = A4,
                rightMargin  = 2*cm,
                leftMargin   = 2*cm,
                topMargin    = 2*cm,
                bottomMargin = 2*cm
            )

            styles   = PDFService._get_styles()
            elements = []

            # Header
            elements += PDFService._build_header(
                styles,
                title    = 'Individual Student Academic Report',
                subtitle = f'{SCHOOL_NAME} • Academic Year {ACADEMIC_YEAR}'
            )

            # ── Student Info Section ────────────────────────────────────────
            elements.append(Paragraph('👤 Student Information', styles['section']))
            elements.append(HRFlowable(
                width='100%', thickness=1,
                color=PRIMARY, spaceAfter=8
            ))

            student_name = f"{student.first_name} {student.last_name}"
            info_data = [
                ['Student Name',    student_name,
                 'Student ID',      student.student_id or 'N/A'],
                ['Grade',           f"Grade {student.grade} - Section {student.section}",
                 'Gender',          student.gender or 'N/A'],
                ['Date of Birth',   str(student.date_of_birth) if student.date_of_birth else 'N/A',
                 'Age',             f"{student.age} years" if student.age else 'N/A'],
                ['Enrollment Date', str(student.enrollment_date) if student.enrollment_date else 'N/A',
                 'Status',          '✅ Active' if student.is_active else '❌ Inactive'],
            ]

            info_table = Table(info_data, colWidths=[4*cm, 4.5*cm, 4*cm, 4.5*cm])
            info_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (0,-1), LIGHT_BLUE),
                ('BACKGROUND', (2,0), (2,-1), LIGHT_BLUE),
                ('FONTNAME',   (0,0), (0,-1), 'Helvetica-Bold'),
                ('FONTNAME',   (2,0), (2,-1), 'Helvetica-Bold'),
                ('FONTSIZE',   (0,0), (-1,-1), 9),
                ('TEXTCOLOR',  (0,0), (0,-1), PRIMARY),
                ('TEXTCOLOR',  (2,0), (2,-1), PRIMARY),
                ('TEXTCOLOR',  (1,0), (1,-1), DARK_GRAY),
                ('TEXTCOLOR',  (3,0), (3,-1), DARK_GRAY),
                ('GRID',       (0,0), (-1,-1), 0.5, MED_GRAY),
                ('ROWBACKGROUNDS', (0,0), (-1,-1), [WHITE, LIGHT_GRAY]),
                ('PADDING',    (0,0), (-1,-1), 8),
                ('VALIGN',     (0,0), (-1,-1), 'MIDDLE'),
            ]))
            elements.append(info_table)
            elements.append(Spacer(1, 0.3*cm))

            # ── Parent Info ─────────────────────────────────────────────────
            elements.append(Paragraph('👨‍👩‍👧 Parent / Guardian Information', styles['section']))
            elements.append(HRFlowable(
                width='100%', thickness=1,
                color=PRIMARY, spaceAfter=8
            ))

            parent_data = [
                ['Parent Name',  student.parent_name  or 'N/A',
                 'Phone',        student.parent_phone or 'N/A'],
                ['Email',        student.parent_email or 'N/A',
                 'Education',    student.parent_education or 'N/A'],
                ['Socioeconomic Status', student.socioeconomic_status or 'N/A',
                 '', ''],
            ]
            parent_table = Table(parent_data, colWidths=[4*cm, 4.5*cm, 4*cm, 4.5*cm])
            parent_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (0,-1), LIGHT_BLUE),
                ('BACKGROUND', (2,0), (2,-1), LIGHT_BLUE),
                ('FONTNAME',   (0,0), (0,-1), 'Helvetica-Bold'),
                ('FONTNAME',   (2,0), (2,-1), 'Helvetica-Bold'),
                ('FONTSIZE',   (0,0), (-1,-1), 9),
                ('TEXTCOLOR',  (0,0), (0,-1), PRIMARY),
                ('TEXTCOLOR',  (2,0), (2,-1), PRIMARY),
                ('GRID',       (0,0), (-1,-1), 0.5, MED_GRAY),
                ('ROWBACKGROUNDS', (0,0), (-1,-1), [WHITE, LIGHT_GRAY]),
                ('PADDING',    (0,0), (-1,-1), 8),
                ('VALIGN',     (0,0), (-1,-1), 'MIDDLE'),
            ]))
            elements.append(parent_table)
            elements.append(Spacer(1, 0.3*cm))

            # ── Academic Performance ────────────────────────────────────────
            elements.append(Paragraph('📊 Academic Performance', styles['section']))
            elements.append(HRFlowable(
                width='100%', thickness=1,
                color=PRIMARY, spaceAfter=8
            ))

            if academic:
                # GPA Summary
                trend_arrow = '📈' if (academic.grade_trend or 0) >= 0 else '📉'
                trend_val   = f"{academic.grade_trend:+.1f}%" if academic.grade_trend else 'N/A'

                gpa_data = [
                    ['Metric', 'Value', 'Metric', 'Value'],
                    ['Current GPA',
                     f"{academic.current_gpa:.1f}%",
                     'Previous GPA',
                     f"{academic.previous_gpa:.1f}%"],
                    ['Grade Trend',
                     f"{trend_arrow} {trend_val}",
                     'Failed Subjects',
                     str(academic.failed_subjects or 0)],
                    ['Submission Rate',
                     f"{academic.assignment_submission_rate:.1f}%",
                     'Semester',
                     academic.semester or 'N/A'],
                ]

                gpa_table = Table(gpa_data, colWidths=[4*cm, 4.5*cm, 4*cm, 4.5*cm])
                gpa_table.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), PRIMARY),
                    ('TEXTCOLOR',  (0,0), (-1,0), WHITE),
                    ('FONTNAME',   (0,0), (-1,0), 'Helvetica-Bold'),
                    ('FONTNAME',   (0,1), (0,-1), 'Helvetica-Bold'),
                    ('FONTNAME',   (2,1), (2,-1), 'Helvetica-Bold'),
                    ('FONTSIZE',   (0,0), (-1,-1), 9),
                    ('TEXTCOLOR',  (0,1), (0,-1), PRIMARY),
                    ('TEXTCOLOR',  (2,1), (2,-1), PRIMARY),
                    ('GRID',       (0,0), (-1,-1), 0.5, MED_GRAY),
                    ('ROWBACKGROUNDS', (0,1), (-1,-1), [WHITE, LIGHT_GRAY]),
                    ('PADDING',    (0,0), (-1,-1), 8),
                    ('ALIGN',      (0,0), (-1,0), 'CENTER'),
                    ('VALIGN',     (0,0), (-1,-1), 'MIDDLE'),
                ]))
                elements.append(gpa_table)
                elements.append(Spacer(1, 0.3*cm))

                # Subject Scores
                elements.append(Paragraph('📚 Subject-wise Scores', styles['section']))
                elements.append(HRFlowable(
                    width='100%', thickness=1,
                    color=PRIMARY, spaceAfter=8
                ))

                subjects = [
                    ('Mathematics',  academic.math_score),
                    ('Science',      academic.science_score),
                    ('English',      academic.english_score),
                    ('Social Studies', academic.social_score),
                    ('Language',     academic.language_score),
                ]

                subj_data = [['Subject', 'Score', 'Grade', 'Status']]
                for subj_name, score in subjects:
                    if score is not None:
                        s    = float(score)
                        # Letter grade
                        if s >= 90:   grade_letter = 'A+'
                        elif s >= 80: grade_letter = 'A'
                        elif s >= 70: grade_letter = 'B+'
                        elif s >= 60: grade_letter = 'B'
                        elif s >= 50: grade_letter = 'C'
                        elif s >= 35: grade_letter = 'D'
                        else:         grade_letter = 'F'

                        status = '✅ Pass' if s >= 35 else '❌ Fail'
                        subj_data.append([
                            subj_name,
                            f"{s:.1f}%",
                            grade_letter,
                            status
                        ])

                subj_table = Table(subj_data, colWidths=[6*cm, 4*cm, 3.5*cm, 3.5*cm])
                subj_table.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), PRIMARY),
                    ('TEXTCOLOR',  (0,0), (-1,0), WHITE),
                    ('FONTNAME',   (0,0), (-1,0), 'Helvetica-Bold'),
                    ('FONTSIZE',   (0,0), (-1,-1), 9),
                    ('GRID',       (0,0), (-1,-1), 0.5, MED_GRAY),
                    ('ROWBACKGROUNDS', (0,1), (-1,-1), [WHITE, LIGHT_GRAY]),
                    ('ALIGN',      (1,0), (-1,-1), 'CENTER'),
                    ('ALIGN',      (0,0), (-1,0), 'CENTER'),
                    ('PADDING',    (0,0), (-1,-1), 8),
                    ('VALIGN',     (0,0), (-1,-1), 'MIDDLE'),
                ]))
                elements.append(subj_table)

            else:
                elements.append(Paragraph(
                    '⚠️ No academic records found for this student.',
                    styles['body']
                ))

            elements.append(Spacer(1, 0.3*cm))

            # ── Attendance Section ──────────────────────────────────────────
            elements.append(Paragraph('📅 Attendance Summary (Last 90 Days)',
                                       styles['section']))
            elements.append(HRFlowable(
                width='100%', thickness=1,
                color=PRIMARY, spaceAfter=8
            ))

            att_color = SUCCESS if att_stats['rate'] >= 75 else DANGER
            att_data  = [
                ['Total School Days', 'Days Present',
                 'Days Absent', 'Attendance Rate'],
                [str(att_stats['total']),
                 str(att_stats['present']),
                 str(att_stats['absent']),
                 f"{att_stats['rate']:.1f}%"]
            ]
            att_table = Table(att_data, colWidths=[4.25*cm]*4)
            att_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), PRIMARY),
                ('TEXTCOLOR',  (0,0), (-1,0), WHITE),
                ('FONTNAME',   (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTNAME',   (0,1), (-1,1), 'Helvetica-Bold'),
                ('FONTSIZE',   (0,0), (-1,-1), 10),
                ('TEXTCOLOR',  (3,1), (3,1),  att_color),
                ('GRID',       (0,0), (-1,-1), 0.5, MED_GRAY),
                ('ALIGN',      (0,0), (-1,-1), 'CENTER'),
                ('PADDING',    (0,0), (-1,-1), 10),
                ('VALIGN',     (0,0), (-1,-1), 'MIDDLE'),
            ]))
            elements.append(att_table)
            elements.append(Spacer(1, 0.3*cm))

            # ── Risk Prediction Section ─────────────────────────────────────
            elements.append(Paragraph('🤖 AI Risk Assessment', styles['section']))
            elements.append(HRFlowable(
                width='100%', thickness=1,
                color=PRIMARY, spaceAfter=8
            ))

            if prediction:
                # risk_label is the human-readable bucket; risk_level is 0–3 int
                _level_names = {0: 'Low', 1: 'Medium', 2: 'High', 3: 'Critical'}
                risk_label = (prediction.risk_label or '').strip() or _level_names.get(
                    int(prediction.risk_level) if prediction.risk_level is not None else 0,
                    'Low'
                )
                risk_color  = RISK_COLORS.get(risk_label, TEXT_GRAY)
                risk_icons  = {
                    'Low':'🟢', 'Medium':'🟡',
                    'High':'🟠', 'Critical':'🔴'
                }
                risk_icon   = risk_icons.get(risk_label, '⚪')
                # Stored as percentage 0–100 (see prediction_service)
                _conf = float(prediction.confidence_score)
                confidence = f"{_conf:.1f}%" if prediction.confidence_score else 'N/A'
                pred_date   = prediction.created_at.strftime('%d %b %Y') \
                            if prediction.created_at else 'N/A'

                risk_data = [
                    ['Risk Level', 'Confidence', 'Assessment Date', 'Recommendation'],
                    [f"{risk_icon} {risk_label}", confidence, pred_date,
                     'Monitor closely' if risk_label in ['High','Critical']
                     else 'Keep up the good work']
                ]
                risk_table = Table(risk_data, colWidths=[4.25*cm]*4)
                risk_table.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), PRIMARY),
                    ('TEXTCOLOR',  (0,0), (-1,0), WHITE),
                    ('FONTNAME',   (0,0), (-1,0), 'Helvetica-Bold'),
                    ('FONTNAME',   (0,1), (-1,1), 'Helvetica-Bold'),
                    ('FONTSIZE',   (0,0), (-1,-1), 9),
                    ('TEXTCOLOR',  (0,1), (0,1),  risk_color),
                    ('GRID',       (0,0), (-1,-1), 0.5, MED_GRAY),
                    ('ALIGN',      (0,0), (-1,-1), 'CENTER'),
                    ('PADDING',    (0,0), (-1,-1), 10),
                    ('VALIGN',     (0,0), (-1,-1), 'MIDDLE'),
                ]))
                elements.append(risk_table)
            else:
                elements.append(Paragraph(
                    '⚠️ No risk prediction available. Run prediction first.',
                    styles['body']
                ))

            # ── Footer ──────────────────────────────────────────────────────
            elements.append(Spacer(1, 0.5*cm))
            elements.append(HRFlowable(
                width='100%', thickness=0.5,
                color=MED_GRAY, spaceAfter=6
            ))
            elements.append(Paragraph(
                f"🏫 {SCHOOL_NAME}  •  ScholarSense v2.0  •  "
                f"Confidential — For Internal Use Only",
                styles['small']
            ))

            # Build PDF
            doc.build(elements)
            return buffer.getvalue()

        finally:
            db.close()

    # ══════════════════════════════════════════════════════════════════════════
    # REPORT 2 — GRADE WISE REPORT
    # ══════════════════════════════════════════════════════════════════════════

    @staticmethod
    def generate_grade_report(grade: int, section: str = None) -> bytes:
        """
        Generate grade/class wise PDF report.
        Returns: PDF as bytes
        """
        db = SessionLocal()
        try:
            # ── Fetch students ───────────────────────────────────────────────
            query = db.query(Student).filter(
                Student.is_active == True,
                Student.grade     == grade
            )
            if section:
                query = query.filter(Student.section == section)

            students = query.order_by(Student.section, Student.first_name).all()

            if not students:
                raise ValueError(f"No students found for Grade {grade}")

            # ── Build PDF ────────────────────────────────────────────────────
            buffer = BytesIO()
            doc    = SimpleDocTemplate(
                buffer,
                pagesize     = A4,
                rightMargin  = 1.5*cm,
                leftMargin   = 1.5*cm,
                topMargin    = 2*cm,
                bottomMargin = 2*cm
            )

            styles   = PDFService._get_styles()
            elements = []

            title_str = f"Grade {grade}"
            if section:
                title_str += f" — Section {section}"

            elements += PDFService._build_header(
                styles,
                title    = f'{title_str} Academic Performance Report',
                subtitle = f'{SCHOOL_NAME} • Academic Year {ACADEMIC_YEAR}'
            )

            # ── Summary stats ────────────────────────────────────────────────
            total      = len(students)
            gpa_list   = []
            risk_counts= {'Low':0,'Medium':0,'High':0,'Critical':0}

            student_rows = []
            for s in students:
                academic = db.query(AcademicRecord).filter(
                    AcademicRecord.student_id == s.id
                ).order_by(AcademicRecord.recorded_date.desc()).first()

                prediction = db.query(RiskPrediction).filter(
                    RiskPrediction.student_id == s.id
                ).order_by(RiskPrediction.created_at.desc()).first()

                att = PDFService._get_attendance_stats(db, s.id, days=30)

                gpa       = float(academic.current_gpa) if academic else 0.0
                _level_names = {0: 'Low', 1: 'Medium', 2: 'High', 3: 'Critical'}
                risk_label= _level_names.get(prediction.risk_level, 'N/A') if prediction else 'N/A'
                gpa_list.append(gpa)

                if risk_label in risk_counts:
                    risk_counts[risk_label] += 1

                risk_icons = {
                    'Low':'🟢','Medium':'🟡',
                    'High':'🟠','Critical':'🔴','N/A':'⚪'
                }

                student_rows.append([
                    f"{s.first_name} {s.last_name}",
                    s.section or 'N/A',
                    s.student_id or 'N/A',
                    f"{gpa:.1f}%",
                    f"{att['rate']:.1f}%",
                    f"{risk_icons.get(risk_label,'⚪')} {risk_label}",
                    str(academic.failed_subjects or 0) if academic else '0'
                ])

            avg_gpa = sum(gpa_list) / len(gpa_list) if gpa_list else 0

            # ── Class summary cards ──────────────────────────────────────────
            elements.append(Paragraph(
                f'📊 Class Summary — Grade {grade}', styles['section']
            ))
            elements.append(HRFlowable(
                width='100%', thickness=1,
                color=PRIMARY, spaceAfter=8
            ))

            summary_data = [
                ['Total Students', 'Average GPA',
                 'High Risk', 'Critical Risk'],
                [str(total),
                 f"{avg_gpa:.1f}%",
                 str(risk_counts.get('High', 0)),
                 str(risk_counts.get('Critical', 0))]
            ]
            summary_table = Table(summary_data, colWidths=[4.5*cm]*4)
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), PRIMARY),
                ('TEXTCOLOR',  (0,0), (-1,0), WHITE),
                ('FONTNAME',   (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTNAME',   (0,1), (-1,1), 'Helvetica-Bold'),
                ('FONTSIZE',   (0,0), (-1,-1), 11),
                ('TEXTCOLOR',  (2,1), (2,1),  WARNING),
                ('TEXTCOLOR',  (3,1), (3,1),  DANGER),
                ('GRID',       (0,0), (-1,-1), 0.5, MED_GRAY),
                ('ALIGN',      (0,0), (-1,-1), 'CENTER'),
                ('PADDING',    (0,0), (-1,-1), 12),
                ('VALIGN',     (0,0), (-1,-1), 'MIDDLE'),
            ]))
            elements.append(summary_table)
            elements.append(Spacer(1, 0.4*cm))

            # ── Student list table ───────────────────────────────────────────
            elements.append(Paragraph(
                '👥 Student Performance List', styles['section']
            ))
            elements.append(HRFlowable(
                width='100%', thickness=1,
                color=PRIMARY, spaceAfter=8
            ))

            headers    = ['Student Name', 'Sec', 'ID',
                          'GPA', 'Attend.', 'Risk', 'Failed']
            table_data = [headers] + student_rows

            col_widths = [5*cm, 1.5*cm, 2.5*cm,
                          2*cm, 2*cm, 3*cm, 1.5*cm]
            stud_table = Table(table_data, colWidths=col_widths,
                               repeatRows=1)

            row_styles = [
                ('BACKGROUND', (0,0), (-1,0), PRIMARY),
                ('TEXTCOLOR',  (0,0), (-1,0), WHITE),
                ('FONTNAME',   (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE',   (0,0), (-1,-1), 8),
                ('GRID',       (0,0), (-1,-1), 0.5, MED_GRAY),
                ('ALIGN',      (1,0), (-1,-1), 'CENTER'),
                ('PADDING',    (0,0), (-1,-1), 6),
                ('VALIGN',     (0,0), (-1,-1), 'MIDDLE'),
                ('ROWBACKGROUNDS', (0,1), (-1,-1), [WHITE, LIGHT_GRAY]),
            ]
            stud_table.setStyle(TableStyle(row_styles))
            elements.append(stud_table)

            # Footer
            elements.append(Spacer(1, 0.5*cm))
            elements.append(HRFlowable(
                width='100%', thickness=0.5,
                color=MED_GRAY, spaceAfter=6
            ))
            elements.append(Paragraph(
                f"🏫 {SCHOOL_NAME}  •  ScholarSense v2.0  •  "
                f"Confidential — For Internal Use Only",
                styles['small']
            ))

            doc.build(elements)
            return buffer.getvalue()

        finally:
            db.close()

    @staticmethod
    def generate_atrisk_report(grade: int = None) -> bytes:
        """
        Generate at-risk students PDF report.
        Returns: PDF as bytes
        """
        db = SessionLocal()
        try:
            # 2=High, 3=Critical
            query = db.query(RiskPrediction).filter(
                RiskPrediction.risk_level.in_([2, 3])
            ).order_by(RiskPrediction.created_at.desc())

            predictions = query.all()

            # Get unique latest prediction per student
            seen     = set()
            filtered = []
            for p in predictions:
                if p.student_id not in seen:
                    student = db.query(Student).filter(
                        Student.id        == p.student_id,
                        Student.is_active == True
                    ).first()
                    if student:
                        if grade is None or student.grade == grade:
                            filtered.append((student, p))
                            seen.add(p.student_id)

            # ── Build PDF ────────────────────────────────────────────────────
            buffer = BytesIO()
            doc    = SimpleDocTemplate(
                buffer,
                pagesize     = A4,
                rightMargin  = 1.5*cm,
                leftMargin   = 1.5*cm,
                topMargin    = 2*cm,
                bottomMargin = 2*cm
            )

            styles   = PDFService._get_styles()
            elements = []

            grade_str = f"Grade {grade}" if grade else "All Grades"
            elements += PDFService._build_header(
                styles,
                title    = f'At-Risk Students Report — {grade_str}',
                subtitle = f'{SCHOOL_NAME} • Academic Year {ACADEMIC_YEAR}'
            )

            if not filtered:
                elements.append(Spacer(1, 1*cm))
                elements.append(Paragraph(
                    '✅ Great news! No high-risk or critical students found.',
                    styles['body']
                ))
            else:
                critical_count = sum(
                    1 for _, p in filtered
                    if str(p.risk_level).lower() in ['3', 'critical']
                )
                high_count = sum(
                    1 for _, p in filtered
                    if str(p.risk_level).lower() in ['2', 'high']
                )

                elements.append(Paragraph(
                    '⚠️ Risk Summary', styles['section']
                ))
                elements.append(HRFlowable(
                    width='100%', thickness=1,
                    color=PRIMARY, spaceAfter=8
                ))

                sum_data = [
                    ['Total At-Risk', 'Critical', 'High Risk', 'Grade Filter'],
                    [str(len(filtered)),
                    str(critical_count),
                    str(high_count),
                    grade_str]
                ]
                sum_table = Table(sum_data, colWidths=[4.5*cm]*4)
                sum_table.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), PRIMARY),
                    ('TEXTCOLOR',  (0,0), (-1,0), WHITE),
                    ('FONTNAME',   (0,0), (-1,-1), 'Helvetica-Bold'),
                    ('FONTSIZE',   (0,0), (-1,-1), 10),
                    ('TEXTCOLOR',  (1,1), (1,1),  DANGER),
                    ('TEXTCOLOR',  (2,1), (2,1),  WARNING),
                    ('GRID',       (0,0), (-1,-1), 0.5, MED_GRAY),
                    ('ALIGN',      (0,0), (-1,-1), 'CENTER'),
                    ('PADDING',    (0,0), (-1,-1), 10),
                ]))
                elements.append(sum_table)
                elements.append(Spacer(1, 0.4*cm))

                # Student detail rows
                elements.append(Paragraph(
                    '🚨 At-Risk Student Details', styles['section']
                ))
                elements.append(HRFlowable(
                    width='100%', thickness=1,
                    color=PRIMARY, spaceAfter=8
                ))

                headers   = ['Student', 'Grade', 'Risk',
                            'GPA', 'Attendance', 'Failed Subj']
                risk_rows = [headers]

                # ✅ Defined OUTSIDE the loop/list
                risk_icons = {
                    '2': '🟠', 'high': '🟠',
                    '3': '🔴', 'critical': '🔴'
                }
                risk_labels = {
                    '2': 'High', 'high': 'High',
                    '3': 'Critical', 'critical': 'Critical'
                }

                for student, pred in filtered:
                    academic = db.query(AcademicRecord).filter(
                        AcademicRecord.student_id == student.id
                    ).order_by(AcademicRecord.recorded_date.desc()).first()

                    att       = PDFService._get_attendance_stats(db, student.id)
                    risk_key = str(pred.risk_level).lower()
                    risk_icon = risk_icons.get(risk_key, '🔴')
                    risk_text = risk_labels.get(risk_key, str(pred.risk_level))

                    risk_rows.append([
                        f"{student.first_name} {student.last_name}",
                        f"Gr.{student.grade}-{student.section}",
                        f"{risk_icon} {risk_text}",
                        f"{float(academic.current_gpa):.1f}%" if academic else 'N/A',
                        f"{att['rate']:.1f}%",
                        str(academic.failed_subjects or 0) if academic else '0'
                    ])

                col_widths = [5.5*cm, 2.5*cm, 3*cm, 2*cm, 2.5*cm, 2.5*cm]
                risk_table = Table(risk_rows,
                                colWidths=col_widths,
                                repeatRows=1)
                risk_table.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), DANGER),
                    ('TEXTCOLOR',  (0,0), (-1,0), WHITE),
                    ('FONTNAME',   (0,0), (-1,0), 'Helvetica-Bold'),
                    ('FONTSIZE',   (0,0), (-1,-1), 9),
                    ('GRID',       (0,0), (-1,-1), 0.5, MED_GRAY),
                    ('ALIGN',      (1,0), (-1,-1), 'CENTER'),
                    ('PADDING',    (0,0), (-1,-1), 7),
                    ('VALIGN',     (0,0), (-1,-1), 'MIDDLE'),
                    ('ROWBACKGROUNDS', (0,1), (-1,-1), [WHITE, LIGHT_GRAY]),
                ]))
                elements.append(risk_table)

            # Footer
            elements.append(Spacer(1, 0.5*cm))
            elements.append(HRFlowable(
                width='100%', thickness=0.5,
                color=MED_GRAY, spaceAfter=6
            ))
            elements.append(Paragraph(
                f"🏫 {SCHOOL_NAME}  •  ScholarSense v2.0  •  "
                f"Confidential — For Internal Use Only",
                styles['small']
            ))

            doc.build(elements)
            return buffer.getvalue()

        finally:
            db.close()
