from .auth import auth_bp
from .dashboard import dashboard_bp
from .patients import patients_bp
from .doctors import doctors_bp
from .visits import visits_bp
from .main import main_bp


def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(patients_bp)
    app.register_blueprint(doctors_bp)
    app.register_blueprint(visits_bp)
    app.register_blueprint(main_bp)
