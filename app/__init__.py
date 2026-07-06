import os
from datetime import datetime

from flask import Flask

from config import Config
from .models import db, login_manager, Role, User
from .routes import register_blueprints


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)

    register_blueprints(app)

    @app.cli.command("init-db")
    def init_db_command():
        """Initialize the database and create a default admin user."""
        with app.app_context():
            db.create_all()
            _seed_roles_and_admin()
            print("Database initialized.")

    return app


def _seed_roles_and_admin():
    role_names = [
        "Administrator",
        "Receptionist",
        "Doctor",
        "Lab Technician",
    ]
    for name in role_names:
        if not Role.query.filter_by(name=name).first():
            db.session.add(Role(name=name))
    db.session.commit()

    admin_role = Role.query.filter_by(name="Administrator").first()
    if not User.query.filter_by(username="admin").first():
        admin = User(
            username="admin",
            role_id=admin_role.id,
            active=True,
            created_at=datetime.utcnow(),
        )
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.commit()
