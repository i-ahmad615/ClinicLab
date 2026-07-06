import re
from datetime import date

from app.models import Patient, Visit, db


CNIC_PATTERN = re.compile(r"^(\d{5}-\d{7}-\d{1}|\d{13})$")
PHONE_PATTERN = re.compile(r"^[0-9+\-\s]{7,20}$")


def normalize_cnic(raw_cnic):
    return re.sub(r"\D", "", raw_cnic or "")


def normalize_phone(raw_phone):
    return re.sub(r"\D", "", raw_phone or "")


def generate_patient_id():
    last_patient = Patient.query.order_by(Patient.id.desc()).first()
    if not last_patient:
        return "PAT000001"
    last_num = int(last_patient.patient_id.replace("PAT", ""))
    return f"PAT{last_num + 1:06d}"


def generate_visit_number():
    last_visit = Visit.query.order_by(Visit.id.desc()).first()
    if not last_visit or not last_visit.visit_number:
        return "VIS000001"
    last_num = int(last_visit.visit_number.replace("VIS", ""))
    return f"VIS{last_num + 1:06d}"


def generate_visit_token(token_date=None, prefix="A"):
    token_date = token_date or date.today()
    last_token = (
        Visit.query.filter(Visit.token_date == token_date)
        .order_by(Visit.token_number.desc())
        .first()
    )
    next_number = 1
    if last_token and last_token.token_number:
        next_number = last_token.token_number + 1
    display = f"{prefix}-{next_number:03d}"
    return prefix, next_number, display


def calculate_age(dob):
    if not dob:
        return None
    today = date.today()
    years = today.year - dob.year
    if (today.month, today.day) < (dob.month, dob.day):
        years -= 1
    return years


def parse_date(value):
    if not value:
        return None
    return date.fromisoformat(value)
