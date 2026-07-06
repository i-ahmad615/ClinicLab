from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import or_

from app.models import Patient, Visit, db
from app.utils.decorators import role_required
from app.utils.helpers import (
    CNIC_PATTERN,
    PHONE_PATTERN,
    calculate_age,
    generate_patient_id,
    normalize_cnic,
    normalize_phone,
    parse_date,
)


patients_bp = Blueprint("patients", __name__, url_prefix="/patients")


@patients_bp.route("/")
@login_required
@role_required(["Administrator", "Receptionist"])
def list_patients():
    query = request.args.get("q", "").strip()
    patients_query = Patient.query

    if query:
        like_query = f"%{query}%"
        normalized_query = normalize_cnic(query)
        normalized_phone = normalize_phone(query)
        filters = [
            Patient.patient_id.ilike(like_query),
            Patient.cnic.ilike(like_query),
            Patient.phone.ilike(like_query),
            Patient.first_name.ilike(like_query),
            Patient.last_name.ilike(like_query),
        ]
        if normalized_query:
            filters.append(Patient.cnic.ilike(f"%{normalized_query}%"))
        if normalized_phone:
            filters.append(Patient.phone.ilike(f"%{normalized_phone}%"))

        patients_query = patients_query.filter(or_(*filters))

    patients = patients_query.order_by(Patient.created_at.desc()).all()
    return render_template("patients/list.html", patients=patients, query=query)


@patients_bp.route("/new", methods=["GET", "POST"])
@login_required
@role_required(["Administrator", "Receptionist"])
def create_patient():
    if request.method == "POST":
        form = request.form
        cnic_raw = form.get("cnic", "").strip()
        phone_raw = form.get("phone", "").strip()

        if not CNIC_PATTERN.match(cnic_raw):
            flash("Invalid CNIC format. Use 13 digits or 5-7-1 format.", "warning")
            return render_template(
                "patients/form.html",
                patient=None,
                patient_id=generate_patient_id(),
            )

        if not PHONE_PATTERN.match(phone_raw):
            flash("Invalid phone number format.", "warning")
            return render_template(
                "patients/form.html",
                patient=None,
                patient_id=generate_patient_id(),
            )

        normalized_cnic = normalize_cnic(cnic_raw)
        normalized_phone = normalize_phone(phone_raw)

        if Patient.query.filter_by(cnic=normalized_cnic).first():
            flash("CNIC already exists.", "danger")
            return render_template(
                "patients/form.html",
                patient=None,
                patient_id=generate_patient_id(),
            )

        patient = Patient(
            patient_id=generate_patient_id(),
            cnic=normalized_cnic,
            first_name=form.get("first_name", "").strip(),
            last_name=form.get("last_name", "").strip(),
            gender=form.get("gender", "").strip(),
            dob=parse_date(form.get("dob")),
            age=int(form.get("age")) if form.get("age") else None,
            phone=normalized_phone,
            emergency_contact=normalize_phone(form.get("emergency_contact")),
            blood_group=form.get("blood_group"),
            address=form.get("address"),
            city=form.get("city"),
            occupation=form.get("occupation"),
            marital_status=form.get("marital_status"),
            known_allergies=form.get("known_allergies"),
            known_diseases=form.get("known_diseases"),
            remarks=form.get("remarks"),
            created_by=current_user.username,
            created_at=datetime.utcnow(),
        )

        if patient.dob:
            patient.age = calculate_age(patient.dob)

        if not patient.first_name or not patient.gender or not patient.phone:
            flash("Please fill in all required fields.", "warning")
            return render_template(
                "patients/form.html",
                patient=None,
                patient_id=generate_patient_id(),
            )

        db.session.add(patient)
        db.session.commit()

        flash("Patient registered successfully.", "success")
        if form.get("action") == "save_create_visit":
            return redirect(url_for("visits.create_visit", patient_id=patient.id))
        return redirect(url_for("patients.list_patients"))

    return render_template(
        "patients/form.html",
        patient=None,
        patient_id=generate_patient_id(),
    )


@patients_bp.route("/<int:patient_id>")
@login_required
@role_required(["Administrator", "Receptionist", "Doctor", "Lab Technician"])
def patient_detail(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    if current_user.role and current_user.role.name == "Doctor":
        if not current_user.doctor_id:
            flash("No doctor profile is linked to this account.", "warning")
            return redirect(url_for("dashboard.index"))
        assigned = Visit.query.filter_by(
            patient_id=patient_id, doctor_id=current_user.doctor_id
        ).first()
        if not assigned:
            flash("You can only access assigned patients.", "danger")
            return redirect(url_for("visits.doctor_queue"))
    visits = Visit.query.filter_by(patient_id=patient_id).order_by(Visit.visit_date.desc()).all()
    return render_template("patients/detail.html", patient=patient, visits=visits)


@patients_bp.route("/<int:patient_id>/edit", methods=["GET", "POST"])
@login_required
@role_required(["Administrator", "Receptionist"])
def edit_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    if request.method == "POST":
        form = request.form
        cnic_raw = form.get("cnic", "").strip()
        phone_raw = form.get("phone", "").strip()

        if not CNIC_PATTERN.match(cnic_raw):
            flash("Invalid CNIC format.", "warning")
            return render_template("patients/form.html", patient=patient, patient_id=patient.patient_id)

        if not PHONE_PATTERN.match(phone_raw):
            flash("Invalid phone number format.", "warning")
            return render_template("patients/form.html", patient=patient, patient_id=patient.patient_id)

        normalized_cnic = normalize_cnic(cnic_raw)
        normalized_phone = normalize_phone(phone_raw)

        existing_cnic = Patient.query.filter_by(cnic=normalized_cnic).first()
        if existing_cnic and existing_cnic.id != patient.id:
            flash("CNIC already exists.", "danger")
            return render_template("patients/form.html", patient=patient, patient_id=patient.patient_id)

        patient.cnic = normalized_cnic
        patient.first_name = form.get("first_name", "").strip()
        patient.last_name = form.get("last_name", "").strip()
        patient.gender = form.get("gender", "").strip()
        patient.dob = parse_date(form.get("dob"))
        patient.age = int(form.get("age")) if form.get("age") else None
        patient.phone = normalized_phone
        patient.emergency_contact = normalize_phone(form.get("emergency_contact"))
        patient.blood_group = form.get("blood_group")
        patient.address = form.get("address")
        patient.city = form.get("city")
        patient.occupation = form.get("occupation")
        patient.marital_status = form.get("marital_status")
        patient.known_allergies = form.get("known_allergies")
        patient.known_diseases = form.get("known_diseases")
        patient.remarks = form.get("remarks")
        patient.updated_at = datetime.utcnow()

        if patient.dob:
            patient.age = calculate_age(patient.dob)

        if not patient.first_name or not patient.gender or not patient.phone:
            flash("Please fill in all required fields.", "warning")
            return render_template("patients/form.html", patient=patient, patient_id=patient.patient_id)

        db.session.commit()
        flash("Patient updated successfully.", "success")
        return redirect(url_for("patients.patient_detail", patient_id=patient.id))

    return render_template("patients/form.html", patient=patient, patient_id=patient.patient_id)


@patients_bp.route("/<int:patient_id>/deactivate", methods=["POST"])
@login_required
@role_required(["Administrator", "Receptionist"])
def deactivate_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    patient.active = False
    patient.updated_at = datetime.utcnow()
    db.session.commit()
    flash("Patient deactivated successfully.", "success")
    return redirect(url_for("patients.list_patients"))
