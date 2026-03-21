# backend/routes/__init__.py
# Registers all route blueprints with the Flask app

from .auth_routes         import auth_bp
from .user_routes         import user_bp
from .student_routes      import student_bp
from .academic_routes     import academic_bp
from .prediction_routes   import prediction_bp
from .attendance_routes   import attendance_bp
from .notification_routes import notification_bp
from .incident_routes     import incident_bp
from .marks_routes        import marks_bp
from .batch_routes        import batch_bp
from .communication_routes import communication_bp
from .analytics_routes    import analytics_bp
from .report_routes       import report_bp


def register_blueprints(app):
    """Register all route blueprints with the Flask app"""
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(academic_bp)
    app.register_blueprint(prediction_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(notification_bp)
    app.register_blueprint(incident_bp)
    app.register_blueprint(marks_bp)
    app.register_blueprint(batch_bp)
    app.register_blueprint(communication_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(report_bp)
