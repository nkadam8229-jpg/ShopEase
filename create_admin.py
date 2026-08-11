from getpass import getpass

from werkzeug.security import generate_password_hash

from app import create_app, db
from app.models import Admin


app = create_app()


with app.app_context():

    print("Create ShopEase Admin")

    full_name = input("Full Name: ").strip()
    email = input("Email: ").strip().lower()

    password = getpass("Password: ")
    confirm_password = getpass("Confirm Password: ")

    if password != confirm_password:
        print("Passwords do not match.")
        exit(1)

    if len(password) < 8:
        print("Password must contain at least 8 characters.")
        exit(1)

    existing_admin = Admin.query.filter_by(
        email=email
    ).first()

    if existing_admin:
        print("An admin with this email already exists.")
        exit(1)

    admin = Admin(
        full_name=full_name,
        email=email,
        password_hash=generate_password_hash(password),
        role="SUPER_ADMIN"
    )

    db.session.add(admin)
    db.session.commit()

    print("Admin created successfully.")