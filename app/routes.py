from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for
)

from flask_wtf.csrf import CSRFProtect
from sqlalchemy import text
from werkzeug.security import check_password_hash, generate_password_hash

from app import db
from app.models import User


main_bp = Blueprint("main", __name__)


# =========================================================
# HOME
# =========================================================

@main_bp.route("/")
def home():
    return render_template("home.html")


# =========================================================
# DATABASE TEST
# =========================================================

@main_bp.route("/db-test")
def database_test():
    try:
        db.session.execute(text("SELECT 1"))
        return "Database connection successful!"
    except Exception as e:
        return f"Database connection failed: {str(e)}", 500


# =========================================================
# REGISTER
# =========================================================

@main_bp.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        # -------------------------
        # Validation
        # -------------------------

        if not full_name:
            flash("Full name is required.", "danger")
            return render_template("register.html")

        if len(full_name) < 2:
            flash("Full name must contain at least 2 characters.", "danger")
            return render_template("register.html")

        if not email or "@" not in email:
            flash("Please enter a valid email address.", "danger")
            return render_template("register.html")

        if not phone.isdigit() or len(phone) != 10:
            flash("Please enter a valid 10-digit phone number.", "danger")
            return render_template("register.html")

        if len(password) < 8:
            flash("Password must contain at least 8 characters.", "danger")
            return render_template("register.html")

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template("register.html")

        # -------------------------
        # Duplicate check
        # -------------------------

        existing_email = User.query.filter_by(email=email).first()

        if existing_email:
            flash("An account with this email already exists.", "danger")
            return render_template("register.html")

        existing_phone = User.query.filter_by(phone=phone).first()

        if existing_phone:
            flash("An account with this phone number already exists.", "danger")
            return render_template("register.html")

        # -------------------------
        # Create user
        # -------------------------

        password_hash = generate_password_hash(password)

        user = User(
            full_name=full_name,
            email=email,
            phone=phone,
            password_hash=password_hash
        )

        try:

            db.session.add(user)
            db.session.commit()

        except Exception:

            db.session.rollback()

            flash(
                "Unable to create your account. Please try again.",
                "danger"
            )

            return render_template("register.html")

        flash(
            "Registration successful. Please login.",
            "success"
        )

        return redirect(url_for("main.login"))

    return render_template("register.html")


# =========================================================
# LOGIN
# =========================================================

@main_bp.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            flash(
                "Email and password are required.",
                "danger"
            )

            return render_template("login.html")

        user = User.query.filter_by(email=email).first()

        if not user:
            flash(
                "Invalid email or password.",
                "danger"
            )

            return render_template("login.html")

        if not user.is_active:
            flash(
                "Your account is currently inactive.",
                "danger"
            )

            return render_template("login.html")

        if not check_password_hash(
            user.password_hash,
            password
        ):
            flash(
                "Invalid email or password.",
                "danger"
            )

            return render_template("login.html")

        # Create login session

        session.clear()

        session["user_id"] = user.id
        session["user_name"] = user.full_name

        flash(
            f"Welcome back, {user.full_name}!",
            "success"
        )

        return redirect(url_for("main.home"))

    return render_template("login.html")


# =========================================================
# LOGOUT
# =========================================================

@main_bp.route("/logout")
def logout():

    session.clear()

    flash(
        "You have been logged out.",
        "success"
    )

    return redirect(url_for("main.home"))