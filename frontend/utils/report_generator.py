"""
Report Generator — Generates downloadable HTML student reports.
"""
from datetime import datetime


def generate_student_report(details: dict) -> str:
    """
    Generate a print-ready HTML report for a student.
    Returns HTML string for st.download_button().
    """
    student_name = f"{details.get('first_name', '')} {details.get('last_name', '')}"
    student_id   = details.get('student_id', 'N/A')
    grade        = f"{details.get('grade', 'N/A')}-{details.get('section', 'N/A')}"
    age          = details.get('age', 'N/A')
    gender       = details.get('gender', 'N/A')
    parent_name  = details.get('parent_name', 'N/A')
    parent_phone = details.get('parent_phone', 'N/A')
    parent_email = details.get('parent_email', 'N/A')
    generated_at = datetime.now().strftime("%d %B %Y, %I:%M %p")

    # ── Academic section ──────────────────────────────────
    academic_html = ""
    if details.get('academic_records'):
        rec = details['academic_records'][0]
        academic_html = f"""
        <h2>📚 Academic Performance</h2>
        <table>
            <tr><th>Semester</th><td>{rec.get('semester', 'N/A')}</td>
                <th>GPA</th><td>{rec.get('current_gpa', 'N/A')}%</td></tr>
            <tr><th>Math</th><td>{rec.get('math_score', 'N/A')}%</td>
                <th>Science</th><td>{rec.get('science_score', 'N/A')}%</td></tr>
            <tr><th>English</th><td>{rec.get('english_score', 'N/A')}%</td>
                <th>Social</th><td>{rec.get('social_score', 'N/A')}%</td></tr>
            <tr><th>Failed Subjects</th><td>{rec.get('failed_subjects', 0)}</td>
                <th>Assignment Rate</th><td>{rec.get('assignment_submission_rate', 'N/A')}%</td></tr>
        </table>
        """
    else:
        academic_html = "<h2>📚 Academic Performance</h2><p>No academic records available.</p>"

    # ── Risk section ──────────────────────────────────────
    risk_html = ""
    if details.get('latest_risk_prediction'):
        pred       = details['latest_risk_prediction']
        risk_label = pred.get('risk_label', 'N/A')
        risk_colors = {
            'Low': '#22543d', 'Medium': '#7c2d12',
            'High': '#742a2a', 'Critical': '#63171b'
        }
        risk_bg = {
            'Low': '#c6f6d5', 'Medium': '#feebc8',
            'High': '#fed7d7', 'Critical': '#feb2b2'
        }
        color = risk_colors.get(risk_label, '#333')
        bg    = risk_bg.get(risk_label, '#eee')
        # AFTER (fixed): Extract to variables BEFORE the f-string
        conf     = float(pred.get('confidence_score')     or 0)
        prob_low = float(pred.get('probability_low')      or 0)
        prob_med = float(pred.get('probability_medium')   or 0)
        prob_hi  = float(pred.get('probability_high')     or 0)
        prob_cri = float(pred.get('probability_critical') or 0)

        risk_html = f"""
        ...
                <td>{conf:.1f}%</td></tr>
            <tr><th>Prob. Low</th><td>{prob_low:.1f}%</td>
                <th>Prob. Medium</th><td>{prob_med:.1f}%</td></tr>
            <tr><th>Prob. High</th><td>{prob_hi:.1f}%</td>
                <th>Prob. Critical</th><td>{prob_cri:.1f}%</td></tr>

        </table>

            <tr><th>Prob. Low</th><td>{pred.get('probability_low', 0):.1f}%</td>
                <th>Prob. Medium</th><td>{pred.get('probability_medium', 0):.1f}%</td></tr>
            <tr><th>Prob. High</th><td>{pred.get('probability_high', 0):.1f}%</td>
                <th>Prob. Critical</th><td>{pred.get('probability_critical', 0):.1f}%</td></tr>
        </table>
        """
    else:
        risk_html = "<h2>🎯 Risk Assessment</h2><p>No risk prediction available.</p>"

    # ── Full HTML ─────────────────────────────────────────
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Student Report — {student_name}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Arial, sans-serif;
                background: #f7fafc; color: #1a202c;
                padding: 2rem; }}
        .header {{ background: linear-gradient(135deg, #1e40af, #3b82f6);
                   color: white; padding: 2rem; border-radius: 12px;
                   margin-bottom: 1.5rem; }}
        .header h1 {{ font-size: 1.8rem; margin-bottom: 0.25rem; }}
        .header p  {{ opacity: 0.85; font-size: 0.95rem; }}
        .badge {{ display: inline-block; background: rgba(255,255,255,0.2);
                  padding: 4px 12px; border-radius: 20px;
                  font-size: 0.85rem; margin-top: 0.5rem; }}
        .section {{ background: white; border-radius: 12px;
                    border: 1px solid #e2e8f0; padding: 1.5rem;
                    margin-bottom: 1.25rem;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.04); }}
        h2 {{ color: #1e40af; font-size: 1.1rem;
              margin-bottom: 1rem; padding-bottom: 0.5rem;
              border-bottom: 2px solid #dbeafe; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 0.6rem 1rem; text-align: left;
                  border-bottom: 1px solid #f0f4f8; }}
        th {{ color: #4a5568; font-size: 0.8rem;
              text-transform: uppercase; letter-spacing: 0.05em;
              width: 20%; background: #f7fafc; }}
        td {{ color: #1a202c; font-weight: 600; }}
        .footer {{ text-align: center; color: #a0aec0;
                   font-size: 0.8rem; margin-top: 2rem; }}
        @media print {{
            body {{ background: white; padding: 1rem; }}
            .section {{ box-shadow: none; }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎓 Student Report</h1>
        <p>{student_name}</p>
        <span class="badge">ID: {student_id} &nbsp;|&nbsp; Grade: {grade}</span>
    </div>

    <div class="section">
        <h2>📋 Personal Information</h2>
        <table>
            <tr><th>Full Name</th><td>{student_name}</td>
                <th>Student ID</th><td>{student_id}</td></tr>
            <tr><th>Grade</th><td>{grade}</td>
                <th>Age</th><td>{age}</td></tr>
            <tr><th>Gender</th><td>{gender}</td>
                <th>Status</th>
                <td>{'🟢 Active' if details.get('is_active', True) else '🔴 Inactive'}</td></tr>
        </table>
    </div>

    <div class="section">
        <h2>👨‍👩‍👦 Parent / Guardian</h2>
        <table>
            <tr><th>Parent Name</th><td>{parent_name}</td>
                <th>Phone</th><td>{parent_phone}</td></tr>
            <tr><th>Email</th><td colspan="3">{parent_email}</td></tr>
        </table>
    </div>

    <div class="section">
        {academic_html}
    </div>

    <div class="section">
        {risk_html}
    </div>

    <div class="footer">
        Generated by ScholarSense AI &nbsp;|&nbsp; {generated_at}
    </div>
</body>
</html>"""

    return html
