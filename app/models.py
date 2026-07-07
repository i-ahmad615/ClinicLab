from datetime import datetime
import sqlite3

from flask_login import LoginManager, UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.engine import Engine


db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message_category = "warning"


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, _):
    if not isinstance(dbapi_connection, sqlite3.Connection):
        return

    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


class Role(db.Model):
    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctors.id"))
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    role = db.relationship("Role")
    doctor = db.relationship("Doctor")

    def set_password(self, password):
        from werkzeug.security import generate_password_hash

        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        from werkzeug.security import check_password_hash

        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return str(self.id)


class Doctor(db.Model):
    __tablename__ = "doctors"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    pmc_number = db.Column(db.String(50), unique=True)
    specialization = db.Column(db.String(120))
    phone = db.Column(db.String(30))
    status = db.Column(db.String(20), default="Active")
    created_by = db.Column(db.String(80))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    visits = db.relationship("Visit", back_populates="doctor", lazy=True)


class Patient(db.Model):
    __tablename__ = "patients"

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.String(20), unique=True, nullable=False)
    cnic = db.Column(db.String(20), unique=True, nullable=True)
    first_name = db.Column(db.String(120), nullable=False)
    last_name = db.Column(db.String(120))
    gender = db.Column(db.String(20), nullable=False)
    dob = db.Column(db.Date)
    age = db.Column(db.Integer)
    phone = db.Column(db.String(30), nullable=False)
    emergency_contact = db.Column(db.String(30))
    blood_group = db.Column(db.String(10))
    address = db.Column(db.String(255))
    city = db.Column(db.String(100))
    occupation = db.Column(db.String(120))
    marital_status = db.Column(db.String(30))
    known_allergies = db.Column(db.String(255))
    known_diseases = db.Column(db.String(255))
    remarks = db.Column(db.String(255))
    active = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.String(80))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    visits = db.relationship("Visit", back_populates="patient", lazy=True)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name or ''}".strip()


class Visit(db.Model):
    __tablename__ = "visits"

    id = db.Column(db.Integer, primary_key=True)
    visit_number = db.Column(db.String(20), unique=True, nullable=False)
    token_prefix = db.Column(db.String(5), default="A")
    token_number = db.Column(db.Integer)
    token_display = db.Column(db.String(20))
    token_date = db.Column(db.Date)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctors.id"), nullable=False)
    department = db.Column(db.String(120))
    reason = db.Column(db.String(255), nullable=False)
    chief_complaint = db.Column(db.String(255))
    clinical_findings = db.Column(db.String(255))
    symptoms = db.Column(db.String(255))
    diagnosis = db.Column(db.String(255))
    prescription_notes = db.Column(db.String(255))
    advice = db.Column(db.String(255))
    visit_remarks = db.Column(db.String(255))
    follow_up_date = db.Column(db.Date)
    status = db.Column(db.String(30), default="Waiting")
    visit_date = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.String(80))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    patient = db.relationship("Patient", back_populates="visits")
    doctor = db.relationship("Doctor", back_populates="visits")


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
