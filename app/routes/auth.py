from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_user, logout_user

from app.models import User


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        remember = bool(request.form.get("remember"))

        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(password):
            flash("Invalid username or password.", "danger")
            return render_template("auth/login.html", show_sidebar=False)
        if not user.active:
            flash("This account is inactive.", "warning")
            return render_template("auth/login.html", show_sidebar=False)

        login_user(user, remember=remember)
        if user.role and user.role.name == "Doctor":
            return redirect(url_for("visits.doctor_dashboard"))
        return redirect(url_for("dashboard.index"))

    return render_template("auth/login.html", show_sidebar=False)


@auth_bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
