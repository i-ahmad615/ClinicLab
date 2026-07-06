from functools import wraps

from flask import flash, redirect, url_for
from flask_login import current_user


def role_required(allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for("auth.login"))
            if current_user.role and current_user.role.name in allowed_roles:
                return view_func(*args, **kwargs)
            flash("You do not have permission to access this page.", "danger")
            return redirect(url_for("dashboard.index"))

        return wrapped_view

    return decorator
