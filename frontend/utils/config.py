"""
ScholarSense - Global Configuration
Single source of truth for all frontend settings
"""
import os

# ── API Configuration ──────────────────────────────────────
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:5000")

# ── Risk Level Colors ──────────────────────────────────────
RISK_COLORS = {
    "Low":      {"bg": "#c6f6d5", "text": "#22543d", "border": "#9ae6b4", "emoji": "🟢"},
    "Medium":   {"bg": "#feebc8", "text": "#7c2d12", "border": "#fbd38d", "emoji": "🟡"},
    "High":     {"bg": "#fed7d7", "text": "#742a2a", "border": "#fc8181", "emoji": "🔴"},
    "Critical": {"bg": "#feb2b2", "text": "#742a2a", "border": "#f56565", "emoji": "⚫"},
}

# ── Page Metadata ──────────────────────────────────────────
PAGES = {
    "dashboard":           {"title": "Dashboard",           "icon": "📊", "section": "Overview"},
    "students":            {"title": "All Students",        "icon": "👥", "section": "Students"},
    "student_profile":     {"title": "Student Profile",     "icon": "👤", "section": "Students"},
    "marks_entry":         {"title": "Marks Entry",         "icon": "📝", "section": "Students"},
    "predictions":         {"title": "Risk Predictions",    "icon": "🎯", "section": "Risk & AI"},
    "batch_analysis":      {"title": "Batch Analysis",      "icon": "🔁", "section": "Risk & AI"},
    "analytics":           {"title": "Analytics",           "icon": "📈", "section": "Risk & AI"},
    "attendance":          {"title": "Attendance",          "icon": "📅", "section": "Behaviour"},
    "incident_logging":    {"title": "Incident Logging",    "icon": "🚨", "section": "Behaviour"},
    "behavioral":          {"title": "Behavioral Dashboard","icon": "🧠", "section": "Behaviour"},
    "notifications":       {"title": "Notifications",       "icon": "🔔", "section": "Communication"},
    "parent_portal":       {"title": "Parent Portal",       "icon": "📧", "section": "Communication"},
    "user_management":     {"title": "User Management",     "icon": "👤", "section": "Admin"},
}

# ── School Info ────────────────────────────────────────────
SCHOOL_NAME    = "Greenwood High School"
ACADEMIC_YEAR  = "2025-26"
APP_NAME       = "ScholarSense"
APP_SUBTITLE   = "AI-Powered Academic Intelligence System"
