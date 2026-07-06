from flask import Blueprint, render_template
from flask_login import login_required

from app.utils.decorators import role_required


main_bp = Blueprint("main", __name__)


@main_bp.route("/module/<module_name>")
@login_required
@role_required(["Administrator", "Receptionist", "Doctor", "Lab Technician"])
def placeholder(module_name):
    return render_template("shared/placeholder.html", module_name=module_name)
