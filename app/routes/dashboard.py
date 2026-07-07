from datetime import date

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import func

from app.models import Doctor, Patient, Role, User, Visit, db
from app.utils.decorators import role_required


dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@dashboard_bp.route("/dashboard")
@login_required
@role_required(["Administrator", "Receptionist", "Doctor", "Lab Technician"])
def index():
    today = date.today()

    role_name = current_user.role.name if current_user.role else ""

    if role_name == "Doctor":
        return redirect(url_for("visits.doctor_dashboard"))

    todays_patients = (
        db.session.query(Patient)
        .filter(func.date(Patient.created_at) == today)
        .count()
    )
    todays_visits = (
        db.session.query(Visit).filter(func.date(Visit.visit_date) == today).count()
    )

    waiting_patients = (
        Visit.query.filter(func.date(Visit.visit_date) == today)
        .filter(Visit.status == "Waiting")
        .count()
    )

    total_patients = Patient.query.count()
    total_doctors = Doctor.query.count()
    total_visits = Visit.query.count()

    recent_patients = Patient.query.order_by(Patient.created_at.desc()).limit(5).all()
    todays_visits_list = (
        Visit.query.filter(func.date(Visit.visit_date) == today)
        .order_by(Visit.visit_date.desc())
        .limit(5)
        .all()
    )

    if role_name == "Receptionist":
        return render_template(
            "dashboard_reception.html",
            todays_patients=todays_patients,
            todays_visits=todays_visits,
            waiting_patients=waiting_patients,
            recent_patients=recent_patients,
            todays_visits_list=todays_visits_list,
        )

    return render_template(
        "dashboard_admin.html",
        total_patients=total_patients,
        todays_visits=todays_visits,
        total_doctors=total_doctors,
        total_visits=total_visits,
        recent_patients=recent_patients,
        todays_visits_list=todays_visits_list,
    )


@dashboard_bp.route("/admin/receptionist", methods=["GET", "POST"])
@login_required
@role_required(["Administrator"])
def receptionist_credentials():
    receptionist_role = Role.query.filter_by(name="Receptionist").first()
    receptionist_user = None
    if receptionist_role:
        receptionist_user = User.query.filter_by(role_id=receptionist_role.id).first()

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Username and password are required.", "warning")
            return render_template(
                "admin/receptionist_credentials.html",
                receptionist_user=receptionist_user,
            )

        existing_user = User.query.filter_by(username=username).first()
        if existing_user and (not receptionist_user or existing_user.id != receptionist_user.id):
            flash("Username already exists.", "danger")
            return render_template(
                "admin/receptionist_credentials.html",
                receptionist_user=receptionist_user,
            )

        if not receptionist_role:
            flash("Receptionist role not found. Please re-run init-db.", "danger")
            return render_template(
                "admin/receptionist_credentials.html",
                receptionist_user=receptionist_user,
            )

        if receptionist_user:
            receptionist_user.username = username
            receptionist_user.set_password(password)
        else:
            receptionist_user = User(
                username=username,
                role_id=receptionist_role.id,
                active=True,
            )
            receptionist_user.set_password(password)
            db.session.add(receptionist_user)

        db.session.commit()
        flash("Receptionist credentials updated.", "success")
        return redirect(url_for("dashboard.receptionist_credentials"))

    return render_template(
        "admin/receptionist_credentials.html",
        receptionist_user=receptionist_user,
    )


@dashboard_bp.route("/admin/account", methods=["GET", "POST"])
@login_required
@role_required(["Administrator"])
def admin_account_credentials():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        current_password = request.form.get("current_password", "")
        new_password = request.form.get("new_password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not username or not current_password:
            flash("Username and current password are required.", "warning")
            return render_template("admin/admin_credentials.html")

        if not current_user.check_password(current_password):
            flash("Current password is incorrect.", "danger")
            return render_template("admin/admin_credentials.html")

        existing_user = User.query.filter_by(username=username).first()
        if existing_user and existing_user.id != current_user.id:
            flash("Username already exists.", "danger")
            return render_template("admin/admin_credentials.html")

        if new_password:
            if len(new_password) < 6:
                flash("New password must be at least 6 characters.", "warning")
                return render_template("admin/admin_credentials.html")
            if new_password != confirm_password:
                flash("New password and confirm password do not match.", "warning")
                return render_template("admin/admin_credentials.html")

        current_user.username = username
        if new_password:
            current_user.set_password(new_password)

        db.session.commit()
        flash("Admin login credentials updated successfully.", "success")
        return redirect(url_for("dashboard.admin_account_credentials"))

    return render_template("admin/admin_credentials.html")
