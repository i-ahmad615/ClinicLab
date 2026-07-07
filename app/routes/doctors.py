from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.models import Doctor, Role, User, db
from app.utils.decorators import role_required


doctors_bp = Blueprint("doctors", __name__, url_prefix="/doctors")


@doctors_bp.route("/")
@login_required
@role_required(["Administrator"])
def list_doctors():
    doctors = Doctor.query.order_by(Doctor.created_at.desc()).all()
    return render_template("doctors/list.html", doctors=doctors)


@doctors_bp.route("/new", methods=["GET", "POST"])
@login_required
@role_required(["Administrator"])
def create_doctor():
    if request.method == "POST":
        form = request.form
        name = form.get("name", "").strip()
        pmc_number = form.get("pmc_number", "").strip()
        username = form.get("username", "").strip()
        password = form.get("password", "")

        if not name:
            flash("Doctor name is required.", "warning")
            return render_template("doctors/form.html", doctor=None)

        if not username or not password:
            flash("Username and password are required for doctor login.", "warning")
            return render_template("doctors/form.html", doctor=None)

        if User.query.filter_by(username=username).first():
            flash("Username already exists.", "danger")
            return render_template("doctors/form.html", doctor=None)

        if pmc_number and Doctor.query.filter_by(pmc_number=pmc_number).first():
            flash("PMC number already exists.", "danger")
            return render_template("doctors/form.html", doctor=None)

        doctor_role = Role.query.filter_by(name="Doctor").first()
        if not doctor_role:
            flash("Doctor role not found. Please re-run init-db.", "danger")
            return render_template("doctors/form.html", doctor=None)

        doctor = Doctor(
            name=name,
            pmc_number=pmc_number or None,
            specialization=form.get("specialization"),
            phone=form.get("phone"),
            status=form.get("status", "Active"),
            created_by=current_user.username,
            created_at=datetime.utcnow(),
        )
        db.session.add(doctor)
        db.session.flush()

        user = User(
            username=username,
            role_id=doctor_role.id,
            doctor_id=doctor.id,
            active=True,
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash("Doctor created successfully.", "success")
        return redirect(url_for("doctors.list_doctors"))

    return render_template("doctors/form.html", doctor=None)


@doctors_bp.route("/<int:doctor_id>/edit", methods=["GET", "POST"])
@login_required
@role_required(["Administrator"])
def edit_doctor(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    linked_user = User.query.filter_by(doctor_id=doctor.id).first()
    if request.method == "POST":
        form = request.form
        name = form.get("name", "").strip()
        pmc_number = form.get("pmc_number", "").strip()
        username = form.get("username", "").strip()
        password = form.get("password", "")

        if not name:
            flash("Doctor name is required.", "warning")
            return render_template("doctors/form.html", doctor=doctor, linked_user=linked_user)

        existing = Doctor.query.filter_by(pmc_number=pmc_number).first()
        if pmc_number and existing and existing.id != doctor.id:
            flash("PMC number already exists.", "danger")
            return render_template("doctors/form.html", doctor=doctor, linked_user=linked_user)

        if username:
            existing_user = User.query.filter_by(username=username).first()
            if existing_user and (not linked_user or existing_user.id != linked_user.id):
                flash("Username already exists.", "danger")
                return render_template(
                    "doctors/form.html", doctor=doctor, linked_user=linked_user
                )

        doctor.name = name
        doctor.pmc_number = pmc_number or None
        doctor.specialization = form.get("specialization")
        doctor.phone = form.get("phone")
        doctor.status = form.get("status", "Active")
        doctor.updated_at = datetime.utcnow()

        if linked_user:
            if username:
                linked_user.username = username
            if password:
                linked_user.set_password(password)
        elif username and password:
            doctor_role = Role.query.filter_by(name="Doctor").first()
            if not doctor_role:
                flash("Doctor role not found. Please re-run init-db.", "danger")
                return render_template(
                    "doctors/form.html", doctor=doctor, linked_user=linked_user
                )
            new_user = User(
                username=username,
                role_id=doctor_role.id,
                doctor_id=doctor.id,
                active=True,
            )
            new_user.set_password(password)
            db.session.add(new_user)

        db.session.commit()
        flash("Doctor updated successfully.", "success")
        return redirect(url_for("doctors.list_doctors"))

    return render_template("doctors/form.html", doctor=doctor, linked_user=linked_user)


@doctors_bp.route("/<int:doctor_id>/deactivate", methods=["POST"])
@login_required
@role_required(["Administrator"])
def toggle_doctor_status(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    doctor.status = "Active" if doctor.status != "Active" else "Inactive"
    doctor.updated_at = datetime.utcnow()

    linked_user = User.query.filter_by(doctor_id=doctor.id).first()
    if linked_user:
        linked_user.active = doctor.status == "Active"

    db.session.commit()
    flash(
        "Doctor activated successfully." if doctor.status == "Active" else "Doctor deactivated successfully.",
        "success",
    )
    return redirect(url_for("doctors.list_doctors"))
