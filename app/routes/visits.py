from datetime import date, datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import case, func

from app.models import Doctor, Patient, Visit, db
from app.utils.decorators import role_required
from app.utils.helpers import generate_visit_number, generate_visit_token, parse_date


visits_bp = Blueprint("visits", __name__, url_prefix="/visits")


@visits_bp.route("/")
@login_required
@role_required(["Administrator", "Receptionist"])
def list_visits():
    visits = Visit.query.order_by(Visit.visit_date.desc()).all()
    return render_template("visits/list.html", visits=visits)


@visits_bp.route("/new", methods=["GET", "POST"])
@login_required
@role_required(["Administrator", "Receptionist"])
def create_visit():
    patient_id = request.args.get("patient_id")
    patients = Patient.query.filter_by(active=True).order_by(Patient.first_name.asc()).all()
    doctors = Doctor.query.filter_by(status="Active").order_by(Doctor.name.asc()).all()
    now = datetime.now()
    visit_number = generate_visit_number()

    if not doctors:
        doctors = Doctor.query.order_by(Doctor.name.asc()).all()
        if not doctors:
            flash("No doctors found. Please add a doctor first.", "warning")
        else:
            flash("No active doctors found. Showing all doctors.", "warning")

    if request.method == "POST":
        form = request.form
        patient_id = form.get("patient_id")
        doctor_id = form.get("doctor_id")
        reason = form.get("reason", "").strip()
        today = date.today()

        if not patient_id or not doctor_id or not reason:
            flash("Please fill in all required fields.", "warning")
            return render_template(
                "visits/form.html",
                patients=patients,
                doctors=doctors,
                selected_patient_id=patient_id,
                visit_number=visit_number,
                visit_date=now.date(),
                visit_time=now.strftime("%H:%M"),
            )

        existing_visit = (
            Visit.query.filter(Visit.patient_id == int(patient_id))
            .filter(func.date(Visit.visit_date) == today)
            .filter(Visit.status.in_(["Waiting", "In Consultation"]))
            .first()
        )
        if existing_visit:
            flash(
                "An active visit already exists for this patient today.",
                "warning",
            )
            return render_template(
                "visits/form.html",
                patients=patients,
                doctors=doctors,
                selected_patient_id=patient_id,
                visit_number=visit_number,
                visit_date=now.date(),
                visit_time=now.strftime("%H:%M"),
            )

        token_prefix, token_number, token_display = generate_visit_token(today)

        visit = Visit(
            visit_number=visit_number,
            token_prefix=token_prefix,
            token_number=token_number,
            token_display=token_display,
            token_date=today,
            patient_id=int(patient_id),
            doctor_id=int(doctor_id),
            department=form.get("department"),
            reason=reason,
            follow_up_date=parse_date(form.get("follow_up_date")),
            status=form.get("status", "Waiting"),
            created_by=current_user.username,
            created_at=datetime.utcnow(),
            visit_date=now,
        )

        db.session.add(visit)
        db.session.commit()
        flash("Visit created successfully.", "success")
        return redirect(url_for("visits.token", visit_id=visit.id))

    return render_template(
        "visits/form.html",
        patients=patients,
        doctors=doctors,
        selected_patient_id=patient_id,
        visit_number=visit_number,
        visit_date=now.date(),
        visit_time=now.strftime("%H:%M"),
    )


@visits_bp.route("/<int:visit_id>/token")
@login_required
@role_required(["Administrator", "Receptionist", "Doctor"])
def token(visit_id):
    visit = Visit.query.get_or_404(visit_id)
    return render_template("visits/token.html", visit=visit, show_sidebar=False)


@visits_bp.route("/queue")
@login_required
@role_required(["Doctor"])
def doctor_queue():
    if not current_user.doctor_id:
        flash("No doctor profile is linked to this account.", "warning")
        return redirect(url_for("dashboard.index"))

    today = date.today()
    status_order = case(
        (Visit.status == "Waiting", 0),
        (Visit.status == "In Consultation", 1),
        (Visit.status == "Completed", 2),
        (Visit.status == "Cancelled", 3),
        else_=4,
    )

    queue = (
        Visit.query.filter(Visit.doctor_id == current_user.doctor_id)
        .filter(func.date(Visit.visit_date) == today)
        .order_by(status_order, Visit.token_number.asc())
        .all()
    )
    return render_template("visits/queue.html", queue=queue)


@visits_bp.route("/<int:visit_id>/consult", methods=["GET", "POST"])
@login_required
@role_required(["Doctor"])
def consult_visit(visit_id):
    visit = Visit.query.get_or_404(visit_id)
    if current_user.doctor_id != visit.doctor_id:
        flash("You can only open visits assigned to you.", "danger")
        return redirect(url_for("visits.doctor_queue"))

    patient = visit.patient
    history = (
        Visit.query.filter(Visit.patient_id == patient.id)
        .order_by(Visit.visit_date.desc())
        .all()
    )

    if request.method == "POST":
        form = request.form
        visit.chief_complaint = form.get("chief_complaint")
        visit.clinical_findings = form.get("clinical_findings")
        visit.diagnosis = form.get("diagnosis")
        visit.prescription_notes = form.get("prescription_notes")
        visit.advice = form.get("advice")
        visit.follow_up_date = parse_date(form.get("follow_up_date"))
        visit.visit_remarks = form.get("visit_remarks")
        visit.updated_at = datetime.utcnow()

        if form.get("action") == "complete":
            visit.status = "Completed"
            flash("Visit completed successfully.", "success")
            db.session.commit()
            return redirect(url_for("patients.patient_detail", patient_id=patient.id))

        visit.status = "In Consultation"
        db.session.commit()
        flash("Draft saved.", "success")
        return redirect(url_for("visits.consult_visit", visit_id=visit.id))

    return render_template(
        "visits/consult.html",
        visit=visit,
        patient=patient,
        history=history,
    )


@visits_bp.route("/doctor-dashboard")
@login_required
@role_required(["Doctor"])
def doctor_dashboard():
    if not current_user.doctor_id:
        flash("No doctor profile is linked to this account.", "warning")
        return redirect(url_for("dashboard.index"))

    today = date.today()
    waiting_count = (
        Visit.query.filter(Visit.doctor_id == current_user.doctor_id)
        .filter(func.date(Visit.visit_date) == today)
        .filter(Visit.status == "Waiting")
        .count()
    )
    completed_today = (
        Visit.query.filter(Visit.doctor_id == current_user.doctor_id)
        .filter(func.date(Visit.visit_date) == today)
        .filter(Visit.status == "Completed")
        .count()
    )
    patients_seen = (
        db.session.query(Visit.patient_id)
        .filter(Visit.doctor_id == current_user.doctor_id)
        .filter(func.date(Visit.visit_date) == today)
        .filter(Visit.status == "Completed")
        .distinct()
        .count()
    )

    queue = (
        Visit.query.filter(Visit.doctor_id == current_user.doctor_id)
        .filter(func.date(Visit.visit_date) == today)
        .order_by(Visit.token_number.asc())
        .all()
    )

    return render_template(
        "dashboard_doctor.html",
        waiting_count=waiting_count,
        completed_today=completed_today,
        patients_seen=patients_seen,
        queue=queue,
    )
