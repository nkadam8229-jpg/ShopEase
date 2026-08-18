from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for
)

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash

from app import db
from app.models import (
    Admin,
    Brand,
    Category,
    Subcategory,
    Product,
    ProductImage,
    ProductSize,
    Banner,
    User,
    Order,
    OrderItem,
    TrafficEvent
)
from app.services.upload_service import upload_image
from app.services.storage_service import StorageService


admin_bp = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin"
)

# =========================================================
# ADMIN AUTHENTICATION GUARD
# =========================================================

@admin_bp.before_request
def require_admin_login():

    allowed_endpoints = {
        "admin.login"
    }

    if request.endpoint in allowed_endpoints:
        return None

    if "admin_id" not in session:
        return redirect(
            url_for("admin.login")
        )

    return None
# =========================================================
# ADMIN LOGIN
# =========================================================

@admin_bp.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            flash(
                "Email and password are required.",
                "danger"
            )
            return render_template("admin_login.html")

        admin = Admin.query.filter_by(email=email).first()

        if not admin:
            flash(
                "Invalid email or password.",
                "danger"
            )
            return render_template("admin_login.html")

        if not admin.is_active:
            flash(
                "This admin account is inactive.",
                "danger"
            )
            return render_template("admin_login.html")

        if not check_password_hash(
            admin.password_hash,
            password
        ):
            flash(
                "Invalid email or password.",
                "danger"
            )
            return render_template("admin_login.html")

        session.clear()

        session["admin_id"] = admin.id
        session["admin_name"] = admin.full_name
        session["admin_role"] = admin.role

        return redirect(url_for("admin.dashboard"))

    return render_template("admin_login.html")


# =========================================================
# ADMIN DASHBOARD
# =========================================================

@admin_bp.route("/dashboard")
def dashboard():

    if "admin_id" not in session:
        return redirect(url_for("admin.login"))

    return render_template(
        "admin/dashboard.html"
    )


# =========================================================
# ADMIN LOGOUT
# =========================================================

@admin_bp.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("admin.login"))


# =========================================================
# CATEGORY LIST
# =========================================================

@admin_bp.route("/categories")
def categories():

    if "admin_id" not in session:
        return redirect(url_for("admin.login"))

    categories = (
        Category.query
        .order_by(Category.created_at.desc())
        .all()
    )

    return render_template(
        "admin/categories.html",
        categories=categories
    )


# =========================================================
# ADD CATEGORY
# =========================================================

@admin_bp.route("/categories/add", methods=["GET", "POST"])
def add_category():

    if "admin_id" not in session:
        return redirect(url_for("admin.login"))

    if request.method == "POST":

        name = request.form.get("name", "").strip()

        image = request.files.get("image")

        if not name:
            flash("Category name is required.", "danger")

            return render_template(
                "admin/category_form.html",
                category=None
            )

        slug = "-".join(name.lower().split())

        existing_category = Category.query.filter(
            db.or_(
                Category.name.ilike(name),
                Category.slug == slug
            )
        ).first()

        if existing_category:
            flash(
                "A category with this name already exists.",
                "danger"
            )

            return render_template(
                "admin/category_form.html",
                category=None
            )

        image_key = None

        if image and image.filename:

            try:

                image_key = upload_image(
                    image,
                    "categories"
                )

            except ValueError as error:

                flash(str(error), "danger")

                return render_template(
                    "admin/category_form.html",
                    category=None
                )

        category = Category(
            name=name,
            slug=slug,
            image_key=image_key,
            is_active=True
        )

        try:

            db.session.add(category)
            db.session.commit()

            flash(
                "Category created successfully.",
                "success"
            )

            return redirect(
                url_for("admin.categories")
            )

        except IntegrityError:

            db.session.rollback()

            # Remove uploaded image if database save fails
            if image_key:

                StorageService().delete(
                    image_key
                )

            flash(
                "Unable to create category.",
                "danger"
            )

            return render_template(
                "admin/category_form.html",
                category=None
            )

    return render_template(
        "admin/category_form.html",
        category=None
    )


# =========================================================
# EDIT CATEGORY
# =========================================================

@admin_bp.route(
    "/categories/<int:category_id>/edit",
    methods=["GET", "POST"]
)
def edit_category(category_id):

    if "admin_id" not in session:
        return redirect(url_for("admin.login"))

    category = db.session.get(
        Category,
        category_id
    )

    if not category:

        flash(
            "Category not found.",
            "danger"
        )

        return redirect(
            url_for("admin.categories")
        )

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        image = request.files.get("image")

        if not name:

            flash(
                "Category name is required.",
                "danger"
            )

            return render_template(
                "admin/category_form.html",
                category=category
            )

        slug = "-".join(
            name.lower().split()
        )

        existing_category = Category.query.filter(
            Category.id != category.id,
            db.or_(
                Category.name.ilike(name),
                Category.slug == slug
            )
        ).first()

        if existing_category:

            flash(
                "Another category with this name already exists.",
                "danger"
            )

            return render_template(
                "admin/category_form.html",
                category=category
            )

        old_image_key = category.image_key
        new_image_key = None

        # Upload new image only if one was selected
        if image and image.filename:

            try:

                new_image_key = upload_image(
                    image,
                    "categories"
                )

            except ValueError as error:

                flash(
                    str(error),
                    "danger"
                )

                return render_template(
                    "admin/category_form.html",
                    category=category
                )

        category.name = name
        category.slug = slug

        if new_image_key:

            category.image_key = new_image_key

        try:

            db.session.commit()

        except IntegrityError:

            db.session.rollback()

            # Remove newly uploaded image if database update fails
            if new_image_key:

                StorageService().delete(
                    new_image_key
                )

            flash(
                "Unable to update category.",
                "danger"
            )

            return render_template(
                "admin/category_form.html",
                category=category
            )

        # Delete old image only after successful DB update
        if new_image_key and old_image_key:

            StorageService().delete(
                old_image_key
            )

        flash(
            "Category updated successfully.",
            "success"
        )

        return redirect(
            url_for("admin.categories")
        )

    return render_template(
        "admin/category_form.html",
        category=category
    )


# =========================================================
# TOGGLE CATEGORY STATUS
# =========================================================

@admin_bp.route(
    "/categories/<int:category_id>/toggle",
    methods=["POST"]
)
def toggle_category(category_id):

    if "admin_id" not in session:
        return redirect(url_for("admin.login"))

    category = db.session.get(
        Category,
        category_id
    )

    if not category:

        flash(
            "Category not found.",
            "danger"
        )

        return redirect(
            url_for("admin.categories")
        )

    category.is_active = not category.is_active

    try:

        db.session.commit()

    except Exception:

        db.session.rollback()

        flash(
            "Unable to update category status.",
            "danger"
        )

        return redirect(
            url_for("admin.categories")
        )

    if category.is_active:

        flash(
            f"{category.name} has been activated.",
            "success"
        )

    else:

        flash(
            f"{category.name} has been deactivated.",
            "success"
        )

    return redirect(
        url_for("admin.categories")
    )



@admin_bp.route(
    "/categories/<int:category_id>/delete",
    methods=["POST"]
)
def delete_category(category_id):

    if "admin_id" not in session:
        return redirect(url_for("admin.login"))

    category = db.session.get(
        Category,
        category_id
    )

    if not category:

        flash(
            "Category not found.",
            "danger"
        )

        return redirect(
            url_for("admin.categories")
        )

    # A category cannot be deleted while it
    # still contains subcategories.
    subcategory_exists = (
        Subcategory.query
        .filter_by(category_id=category.id)
        .first()
    )

    if subcategory_exists:

        flash(
            "Category cannot be deleted because it contains subcategories. "
            "Delete the subcategories first.",
            "danger"
        )

        return redirect(
            url_for("admin.categories")
        )

    image_key = category.image_key

    try:

        db.session.delete(category)
        db.session.commit()

    except IntegrityError:

        db.session.rollback()

        flash(
            "Category could not be deleted because it is being used by another record.",
            "danger"
        )

        return redirect(
            url_for("admin.categories")
        )

    # Delete the category image only after
    # successful database deletion.
    if image_key:

        StorageService().delete(
            image_key
        )

    flash(
        "Category permanently deleted.",
        "success"
    )

    return redirect(
        url_for("admin.categories")
    )


# =========================================================
# SUBCATEGORY LIST
# =========================================================

@admin_bp.route("/subcategories")
def subcategories():

    if "admin_id" not in session:
        return redirect(url_for("admin.login"))

    subcategories = (
        Subcategory.query
        .order_by(Subcategory.created_at.desc())
        .all()
    )

    return render_template(
        "admin/subcategories.html",
        subcategories=subcategories
    )

# =========================================================
# ADD SUBCATEGORY
# =========================================================

@admin_bp.route(
    "/subcategories/add",
    methods=["GET", "POST"]
)
def add_subcategory():

    if "admin_id" not in session:
        return redirect(url_for("admin.login"))

    categories = (
        Category.query
        .filter_by(is_active=True)
        .order_by(Category.name.asc())
        .all()
    )

    if request.method == "POST":

        category_id = request.form.get(
            "category_id",
            ""
        ).strip()

        name = request.form.get(
            "name",
            ""
        ).strip()

        image = request.files.get("image")

        if not category_id:

            flash(
                "Category is required.",
                "danger"
            )

            return render_template(
                "admin/subcategory_form.html",
                subcategory=None,
                categories=categories
            )

        if not name:

            flash(
                "Subcategory name is required.",
                "danger"
            )

            return render_template(
                "admin/subcategory_form.html",
                subcategory=None,
                categories=categories
            )

        category = db.session.get(
            Category,
            int(category_id)
        )

        if not category or not category.is_active:

            flash(
                "Selected category is invalid.",
                "danger"
            )

            return render_template(
                "admin/subcategory_form.html",
                subcategory=None,
                categories=categories
            )

        slug = "-".join(
            name.lower().split()
        )

        existing_subcategory = Subcategory.query.filter(
            db.or_(
                Subcategory.name.ilike(name),
                Subcategory.slug == slug
            )
        ).first()

        if existing_subcategory:

            flash(
                "A subcategory with this name already exists.",
                "danger"
            )

            return render_template(
                "admin/subcategory_form.html",
                subcategory=None,
                categories=categories
            )

        image_key = None

        if image and image.filename:

            try:

                image_key = upload_image(
                    image,
                    "subcategories"
                )

            except ValueError as error:

                flash(
                    str(error),
                    "danger"
                )

                return render_template(
                    "admin/subcategory_form.html",
                    subcategory=None,
                    categories=categories
                )

        subcategory = Subcategory(
            category_id=int(category_id),
            name=name,
            slug=slug,
            image_key=image_key,
            is_active=True
        )

        try:

            db.session.add(subcategory)
            db.session.commit()

        except IntegrityError:

            db.session.rollback()

            if image_key:

                StorageService().delete(
                    image_key
                )

            flash(
                "Unable to create subcategory.",
                "danger"
            )

            return render_template(
                "admin/subcategory_form.html",
                subcategory=None,
                categories=categories
            )

        flash(
            "Subcategory created successfully.",
            "success"
        )

        return redirect(
            url_for("admin.subcategories")
        )

    return render_template(
        "admin/subcategory_form.html",
        subcategory=None,
        categories=categories
    )


@admin_bp.route(
    "/subcategories/<int:subcategory_id>/image"
)
def subcategory_image(subcategory_id):

    if "admin_id" not in session:
        return redirect(url_for("admin.login"))

    subcategory = db.session.get(
        Subcategory,
        subcategory_id
    )

    if not subcategory or not subcategory.image_key:
        return "", 404


    storage = StorageService()

    if not storage.exists(subcategory.image_key):
        return "", 404

    image_file = storage.get_file(
        subcategory.image_key
    )

    from flask import send_file

    return send_file(
        image_file,
        mimetype="image/webp"
    )

# =========================================================
# EDIT SUBCATEGORY
# =========================================================

@admin_bp.route(
    "/subcategories/<int:subcategory_id>/edit",
    methods=["GET", "POST"]
)
def edit_subcategory(subcategory_id):

    if "admin_id" not in session:
        return redirect(url_for("admin.login"))

    subcategory = db.session.get(
        Subcategory,
        subcategory_id
    )

    if not subcategory:

        flash(
            "Subcategory not found.",
            "danger"
        )

        return redirect(
            url_for("admin.subcategories")
        )

    categories = (
        Category.query
        .filter_by(is_active=True)
        .order_by(Category.name.asc())
        .all()
    )

    if request.method == "POST":

        category_id = request.form.get(
            "category_id",
            ""
        ).strip()

        name = request.form.get(
            "name",
            ""
        ).strip()

        image = request.files.get("image")

        if not category_id:

            flash(
                "Category is required.",
                "danger"
            )

            return render_template(
                "admin/subcategory_form.html",
                subcategory=subcategory,
                categories=categories
            )

        if not name:

            flash(
                "Subcategory name is required.",
                "danger"
            )

            return render_template(
                "admin/subcategory_form.html",
                subcategory=subcategory,
                categories=categories
            )

        category = db.session.get(
            Category,
            int(category_id)
        )

        if not category or not category.is_active:

            flash(
                "Selected category is invalid.",
                "danger"
            )

            return render_template(
                "admin/subcategory_form.html",
                subcategory=subcategory,
                categories=categories
            )

        slug = "-".join(
            name.lower().split()
        )

        existing_subcategory = Subcategory.query.filter(
            Subcategory.id != subcategory.id,
            db.or_(
                Subcategory.name.ilike(name),
                Subcategory.slug == slug
            )
        ).first()

        if existing_subcategory:

            flash(
                "Another subcategory with this name already exists.",
                "danger"
            )

            return render_template(
                "admin/subcategory_form.html",
                subcategory=subcategory,
                categories=categories
            )

        old_image_key = subcategory.image_key
        new_image_key = None

        # Upload a new image only if selected
        if image and image.filename:

            try:

                new_image_key = upload_image(
                    image,
                    "subcategories"
                )

            except ValueError as error:

                flash(
                    str(error),
                    "danger"
                )

                return render_template(
                    "admin/subcategory_form.html",
                    subcategory=subcategory,
                    categories=categories
                )

        subcategory.category_id = int(category_id)
        subcategory.name = name
        subcategory.slug = slug

        if new_image_key:

            subcategory.image_key = new_image_key

        try:

            db.session.commit()

        except IntegrityError:

            db.session.rollback()

            # Delete newly uploaded image if DB update fails
            if new_image_key:

                StorageService().delete(
                    new_image_key
                )

            flash(
                "Unable to update subcategory.",
                "danger"
            )

            return render_template(
                "admin/subcategory_form.html",
                subcategory=subcategory,
                categories=categories
            )

        # Delete old image only after DB update succeeds
        if new_image_key and old_image_key:

            StorageService().delete(
                old_image_key
            )

        flash(
            "Subcategory updated successfully.",
            "success"
        )

        return redirect(
            url_for("admin.subcategories")
        )

    return render_template(
        "admin/subcategory_form.html",
        subcategory=subcategory,
        categories=categories
    )

# =========================================================
# TOGGLE SUBCATEGORY STATUS
# =========================================================

@admin_bp.route(
    "/subcategories/<int:subcategory_id>/toggle",
    methods=["POST"]
)
def toggle_subcategory(subcategory_id):

    if "admin_id" not in session:
        return redirect(url_for("admin.login"))

    subcategory = db.session.get(
        Subcategory,
        subcategory_id
    )

    if not subcategory:

        flash(
            "Subcategory not found.",
            "danger"
        )

        return redirect(
            url_for("admin.subcategories")
        )

    subcategory.is_active = not subcategory.is_active

    try:

        db.session.commit()

    except Exception:

        db.session.rollback()

        flash(
            "Unable to update subcategory status.",
            "danger"
        )

        return redirect(
            url_for("admin.subcategories")
        )

    if subcategory.is_active:

        flash(
            f"{subcategory.name} has been activated.",
            "success"
        )

    else:

        flash(
            f"{subcategory.name} has been deactivated.",
            "success"
        )

    return redirect(
        url_for("admin.subcategories")
    )



@admin_bp.route(
    "/subcategories/<int:subcategory_id>/delete",
    methods=["POST"]
)
def delete_subcategory(subcategory_id):

    if "admin_id" not in session:
        return redirect(url_for("admin.login"))

    subcategory = db.session.get(
        Subcategory,
        subcategory_id
    )

    if not subcategory:

        flash(
            "Subcategory not found.",
            "danger"
        )

        return redirect(
            url_for("admin.subcategories")
        )

    # -----------------------------------------------------
    # PRODUCT DEPENDENCY CHECK
    # -----------------------------------------------------

    product_exists = (
        Product.query
        .filter_by(
            subcategory_id=subcategory.id
        )
        .first()
    )

    if product_exists:

        flash(
            "Subcategory cannot be deleted because it is "
            "being used by one or more products. "
            "Remove or reassign those products first.",
            "danger"
        )

        return redirect(
            url_for("admin.subcategories")
        )

    image_key = subcategory.image_key

    try:

        db.session.delete(subcategory)
        db.session.commit()

    except IntegrityError:

        db.session.rollback()

        flash(
            "Subcategory could not be deleted because it is being used by another record.",
            "danger"
        )

        return redirect(
            url_for("admin.subcategories")
        )

    # Delete image only after successful database deletion
    if image_key:

        StorageService().delete(
            image_key
        )

    flash(
        "Subcategory permanently deleted.",
        "success"
    )

    return redirect(
        url_for("admin.subcategories")
    )
# =========================================================
# BRAND LIST
# =========================================================

@admin_bp.route("/brands")
def brands():

    if "admin_id" not in session:
        return redirect(url_for("admin.login"))

    brands = (
        Brand.query
        .order_by(Brand.created_at.desc())
        .all()
    )

    return render_template(
        "admin/brands.html",
        brands=brands
    )


# =========================================================
# ADD BRAND
# =========================================================

# =========================================================
# ADD BRAND
# =========================================================

@admin_bp.route(
    "/brands/add",
    methods=["GET", "POST"]
)
def add_brand():

    if "admin_id" not in session:
        return redirect(url_for("admin.login"))

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        if not name:

            flash(
                "Brand name is required.",
                "danger"
            )

            return render_template(
                "admin/brand_form.html",
                brand=None
            )

        slug = "-".join(
            name.lower().split()
        )

        existing_brand = Brand.query.filter(
            db.or_(
                Brand.name.ilike(name),
                Brand.slug == slug
            )
        ).first()

        if existing_brand:

            flash(
                "A brand with this name already exists.",
                "danger"
            )

            return render_template(
                "admin/brand_form.html",
                brand=None
            )

        logo_key = None

        logo_file = request.files.get("logo")

        if logo_file and logo_file.filename:

            try:

                logo_key = upload_image(
                    logo_file,
                    "brands"
                )

            except ValueError as e:

                flash(
                    str(e),
                    "danger"
                )

                return render_template(
                    "admin/brand_form.html",
                    brand=None
                )

            except Exception:

                flash(
                    "Unable to upload brand logo.",
                    "danger"
                )

                return render_template(
                    "admin/brand_form.html",
                    brand=None
                )

        brand = Brand(
            name=name,
            slug=slug,
            logo_key=logo_key,
            is_active=True
        )

        try:

            db.session.add(brand)
            db.session.commit()

            flash(
                "Brand created successfully.",
                "success"
            )

            return redirect(
                url_for("admin.brands")
            )

        except IntegrityError:

            db.session.rollback()

            flash(
                "Unable to create brand.",
                "danger"
            )

            return render_template(
                "admin/brand_form.html",
                brand=None
            )

    return render_template(
        "admin/brand_form.html",
        brand=None
    )


# =========================================================
# EDIT BRAND
# =========================================================

@admin_bp.route(
    "/brands/<int:brand_id>/edit",
    methods=["GET", "POST"]
)
def edit_brand(brand_id):

    if "admin_id" not in session:
        return redirect(url_for("admin.login"))

    brand = db.session.get(
        Brand,
        brand_id
    )

    if not brand:

        flash(
            "Brand not found.",
            "danger"
        )

        return redirect(
            url_for("admin.brands")
        )

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        if not name:

            flash(
                "Brand name is required.",
                "danger"
            )

            return render_template(
                "admin/brand_form.html",
                brand=brand
            )

        slug = "-".join(
            name.lower().split()
        )

        existing_brand = Brand.query.filter(
            Brand.id != brand.id,
            db.or_(
                Brand.name.ilike(name),
                Brand.slug == slug
            )
        ).first()

        if existing_brand:

            flash(
                "Another brand with this name already exists.",
                "danger"
            )

            return render_template(
                "admin/brand_form.html",
                brand=brand
            )

        brand.name = name
        brand.slug = slug

        logo_file = request.files.get("logo")

        if logo_file and logo_file.filename:

            try:

                new_logo_key = upload_image(
                    logo_file,
                    "brands"
                )

                brand.logo_key = new_logo_key

            except ValueError as e:

                flash(
                    str(e),
                    "danger"
                )

                return render_template(
                    "admin/brand_form.html",
                    brand=brand
                )

            except Exception:

                flash(
                    "Unable to upload brand logo.",
                    "danger"
                )

                return render_template(
                    "admin/brand_form.html",
                    brand=brand
                )

        try:

            db.session.commit()

            flash(
                "Brand updated successfully.",
                "success"
            )

            return redirect(
                url_for("admin.brands")
            )

        except IntegrityError:

            db.session.rollback()

            flash(
                "Unable to update brand.",
                "danger"
            )

            return render_template(
                "admin/brand_form.html",
                brand=brand
            )

    return render_template(
        "admin/brand_form.html",
        brand=brand
    )

    # =========================================================
# TOGGLE BRAND STATUS
# =========================================================

@admin_bp.route(
    "/brands/<int:brand_id>/toggle",
    methods=["POST"]
)
def toggle_brand(brand_id):

    if "admin_id" not in session:
        return redirect(url_for("admin.login"))

    brand = db.session.get(
        Brand,
        brand_id
    )

    if not brand:

        flash(
            "Brand not found.",
            "danger"
        )

        return redirect(
            url_for("admin.brands")
        )

    brand.is_active = not brand.is_active

    try:

        db.session.commit()

    except Exception:

        db.session.rollback()

        flash(
            "Unable to update brand status.",
            "danger"
        )

        return redirect(
            url_for("admin.brands")
        )

    if brand.is_active:

        flash(
            f"{brand.name} has been activated.",
            "success"
        )

    else:

        flash(
            f"{brand.name} has been deactivated.",
            "success"
        )

    return redirect(
        url_for("admin.brands")
    )

# =========================================================
# DELETE BRAND
# =========================================================

@admin_bp.route(
    "/brands/<int:brand_id>/delete",
    methods=["POST"]
)
def delete_brand(brand_id):

    if "admin_id" not in session:
        return redirect(url_for("admin.login"))

    brand = db.session.get(
        Brand,
        brand_id
    )

    if not brand:

        flash(
            "Brand not found.",
            "danger"
        )

        return redirect(
            url_for("admin.brands")
        )

    # -----------------------------------------------------
    # PRODUCT DEPENDENCY CHECK
    # -----------------------------------------------------

    product_exists = (
        Product.query
        .filter_by(
            brand_id=brand.id
        )
        .first()
    )

    if product_exists:

        flash(
            "Brand cannot be deleted because it is "
            "being used by one or more products. "
            "Remove or reassign those products first.",
            "danger"
        )

        return redirect(
            url_for("admin.brands")
        )

    logo_key = brand.logo_key

    try:

        db.session.delete(brand)
        db.session.commit()

    except IntegrityError:

        db.session.rollback()

        flash(
            "Brand could not be deleted because it is being used by another record.",
            "danger"
        )

        return redirect(
            url_for("admin.brands")
        )

    # Delete logo only after successful database deletion
    if logo_key:

        StorageService().delete(
            logo_key
        )

    flash(
        "Brand permanently deleted.",
        "success"
    )

    return redirect(
        url_for("admin.brands")
    )

@admin_bp.route("/categories/<int:category_id>/image")
def category_image(category_id):

    if "admin_id" not in session:
        return redirect(url_for("admin.login"))

    category = db.session.get(
        Category,
        category_id
    )

    if not category or not category.image_key:
        return "", 404

    storage = StorageService()

    if not storage.exists(category.image_key):
        return "", 404

    image_file = storage.get_file(
        category.image_key
    )

    from flask import send_file

    return send_file(
        image_file,
        mimetype="image/webp"
    )

# =========================================================
# BRAND IMAGE
# =========================================================

@admin_bp.route("/brands/<int:brand_id>/image")
def brand_image(brand_id):

    if "admin_id" not in session:
        return redirect(url_for("admin.login"))

    brand = db.session.get(
        Brand,
        brand_id
    )

    if not brand or not brand.logo_key:
        return "", 404

    storage = StorageService()

    if not storage.exists(brand.logo_key):
        return "", 404

    image_file = storage.get_file(
        brand.logo_key
    )

    from flask import send_file

    return send_file(
        image_file,
        mimetype="image/webp"
    )


# =========================================================
# PRODUCT LIST
# =========================================================

@admin_bp.route("/products")
def products():

    if "admin_id" not in session:
        return redirect(url_for("admin.login"))

    products = (
        Product.query
        .order_by(
            Product.created_at.desc()
        )
        .all()
    )

    categories = (
        Category.query
        .order_by(
            Category.name.asc()
        )
        .all()
    )

    subcategories = (
        Subcategory.query
        .order_by(
            Subcategory.name.asc()
        )
        .all()
    )

    brands = (
        Brand.query
        .order_by(
            Brand.name.asc()
        )
        .all()
    )

    return render_template(
        "admin/products.html",
        products=products,
        categories=categories,
        subcategories=subcategories,
        brands=brands
    )


# =========================================================
# PRODUCT SIZE VALIDATION
# =========================================================

def parse_variant_specifications(
    raw_specifications,
    variant_name
):
    """
    Convert the admin variant specification textarea into
    a JSON-compatible dictionary.

    Expected format:

    Processor: Intel Core i7
    GPU: RTX 4050
    RAM: 16GB
    Storage: 1TB
    """

    specifications = {}

    if not raw_specifications:
        return None

    for line in raw_specifications.splitlines():

        line = line.strip()

        if not line:
            continue

        if ":" not in line:

            raise ValueError(
                f"Invalid specification format for "
                f"variant '{variant_name}'. "
                f"Use 'Name: Value' on each line."
            )

        key, value = line.split(
            ":",
            1
        )

        key = key.strip()
        value = value.strip()

        if not key or not value:

            raise ValueError(
                f"Invalid specification format for "
                f"variant '{variant_name}'. "
                f"Both name and value are required."
            )

        specifications[key] = value

    if not specifications:
        return None

    return specifications

def get_product_sizes_from_form():

    product_size_ids = request.form.getlist(
        "product_size_id[]"
    )
    size_names = request.form.getlist(
        "size_name[]"
    )

    size_prices = request.form.getlist(
        "size_price[]"
    )

    size_quantities = request.form.getlist(
        "size_quantity[]"
    )

    size_descriptions = request.form.getlist(
        "size_description[]"
    )

    size_specifications = request.form.getlist(
        "size_specifications[]"
    )

    if (
    len(product_size_ids)
    != len(size_names)
    or
    len(size_names)
    != len(size_prices)
    or
    len(size_names)
    != len(size_quantities)
    or
    len(size_names)
    != len(size_descriptions)
    or
    len(size_names)
    != len(size_specifications)
):

        raise ValueError(
            "Invalid size / variant inventory data."
        )

    sizes = []
    used_sizes = set()

    for (
        raw_product_size_id,
        raw_name,
        raw_price,
        raw_quantity,
        raw_description,
        raw_specifications
    ) in zip(
        product_size_ids,
        size_names,
        size_prices,
        size_quantities,
        size_descriptions,
        size_specifications
    ):

        size = raw_name.strip()

        # -------------------------------------------------
        # EXISTING VARIANT ID
        # -------------------------------------------------

        product_size_id = (
            int(raw_product_size_id)
            if raw_product_size_id.strip()
            else None
        )

        # Ignore completely empty rows.
        if not size:
            continue

        normalized_size = size.lower()

        # -------------------------------------------------
        # DUPLICATE SIZE / VARIANT VALIDATION
        # -------------------------------------------------

        if normalized_size in used_sizes:

            raise ValueError(
                f"Duplicate size / variant "
                f"'{size}' is not allowed."
            )

        used_sizes.add(
            normalized_size
        )


        # -------------------------------------------------
        # VARIANT PRICE
        # -------------------------------------------------

        try:

            price = float(
                raw_price
            )

        except (
            ValueError,
            TypeError
        ):

            raise ValueError(
                f"Invalid price for "
                f"size / variant '{size}'."
            )

        if price <= 0:

            raise ValueError(
                f"Price for size / variant "
                f"'{size}' must be greater than 0."
            )


        # -------------------------------------------------
        # VARIANT QUANTITY
        # -------------------------------------------------

        try:

            quantity = int(
                raw_quantity
            )

        except (
            ValueError,
            TypeError
        ):

            raise ValueError(
                f"Invalid quantity for "
                f"size / variant '{size}'."
            )

        if quantity < 0:

            raise ValueError(
                f"Quantity for size / variant "
                f"'{size}' cannot be negative."
            )


        # -------------------------------------------------
        # VARIANT DESCRIPTION
        # -------------------------------------------------

        description = (
            raw_description.strip()
            or None
        )


        # -------------------------------------------------
        # VARIANT SPECIFICATIONS
        # -------------------------------------------------

        specifications = (
            parse_variant_specifications(
                raw_specifications,
                size
            )
        )

        # -------------------------------------------------
        # ADD VARIANT
        # -------------------------------------------------

        sizes.append(
            {
                "product_size_id": product_size_id,
                "size": size,
                "price": price,
                "quantity": quantity,
                "description": description,
                "specifications": specifications
            }
        )


    if not sizes:

        raise ValueError(
            "Add at least one size / variant."
        )


    total_quantity = sum(
        item["quantity"]
        for item in sizes
    )


    return sizes, total_quantity
# =========================================================
# NEW PRODUCT SIZE / VARIANT VALIDATION
# =========================================================

def get_new_product_sizes_from_form():

    size_names = request.form.getlist(
        "size_name[]"
    )

    size_prices = request.form.getlist(
        "size_price[]"
    )

    size_quantities = request.form.getlist(
        "size_quantity[]"
    )

    size_descriptions = request.form.getlist(
        "size_description[]"
    )

    size_specifications = request.form.getlist(
        "size_specifications[]"
    )

    if (
        len(size_names)
        != len(size_prices)
        or
        len(size_names)
        != len(size_quantities)
        or
        len(size_names)
        != len(size_descriptions)
        or
        len(size_names)
        != len(size_specifications)
    ):

        raise ValueError(
            "Invalid size / variant inventory data."
        )

    sizes = []
    used_sizes = set()

    for (
        raw_name,
        raw_price,
        raw_quantity,
        raw_description,
        raw_specifications
    ) in zip(
        size_names,
        size_prices,
        size_quantities,
        size_descriptions,
        size_specifications
    ):

        size = raw_name.strip()

        # Ignore completely empty rows.
        if not size:
            continue

        normalized_size = size.lower()

        # -------------------------------------------------
        # DUPLICATE SIZE / VARIANT VALIDATION
        # -------------------------------------------------

        if normalized_size in used_sizes:

            raise ValueError(
                f"Duplicate size / variant "
                f"'{size}' is not allowed."
            )

        used_sizes.add(
            normalized_size
        )


        # -------------------------------------------------
        # VARIANT PRICE
        # -------------------------------------------------

        try:

            price = float(
                raw_price
            )

        except (
            ValueError,
            TypeError
        ):

            raise ValueError(
                f"Invalid price for "
                f"size / variant '{size}'."
            )

        if price <= 0:

            raise ValueError(
                f"Price for size / variant "
                f"'{size}' must be greater than 0."
            )


        # -------------------------------------------------
        # VARIANT QUANTITY
        # -------------------------------------------------

        try:

            quantity = int(
                raw_quantity
            )

        except (
            ValueError,
            TypeError
        ):

            raise ValueError(
                f"Invalid quantity for "
                f"size / variant '{size}'."
            )

        if quantity < 0:

            raise ValueError(
                f"Quantity for size / variant "
                f"'{size}' cannot be negative."
            )


        # -------------------------------------------------
        # VARIANT DESCRIPTION
        # -------------------------------------------------

        description = (
            raw_description.strip()
            or None
        )


        # -------------------------------------------------
        # VARIANT SPECIFICATIONS
        # -------------------------------------------------

        specifications = (
            parse_variant_specifications(
                raw_specifications,
                size
            )
        )


        # -------------------------------------------------
        # ADD NEW VARIANT
        # -------------------------------------------------

        sizes.append(
            {
                "product_size_id": None,
                "size": size,
                "price": price,
                "quantity": quantity,
                "description": description,
                "specifications": specifications
            }
        )


    if not sizes:

        raise ValueError(
            "Add at least one size / variant."
        )


    total_quantity = sum(
        item["quantity"]
        for item in sizes
    )


    return sizes, total_quantity
# =========================================================
# ADD PRODUCT
# =========================================================

@admin_bp.route(
    "/products/add",
    methods=["GET", "POST"]
)
def add_product():

    if "admin_id" not in session:
        return redirect(url_for("admin.login"))

    categories = (
        Category.query
        .filter_by(is_active=True)
        .order_by(Category.name.asc())
        .all()
    )

    subcategories = (
        Subcategory.query
        .filter_by(is_active=True)
        .order_by(Subcategory.name.asc())
        .all()
    )

    brands = (
        Brand.query
        .filter_by(is_active=True)
        .order_by(Brand.name.asc())
        .all()
    )

    if request.method == "POST":

        category_id = request.form.get(
            "category_id",
            ""
        ).strip()

        subcategory_id = request.form.get(
            "subcategory_id",
            ""
        ).strip()

        brand_id = request.form.get(
            "brand_id",
            ""
        ).strip()

        sku = request.form.get(
            "sku",
            ""
        ).strip().upper()

        name = request.form.get(
            "name",
            ""
        ).strip()

        description = request.form.get(
            "description",
            ""
        ).strip()

        specifications_text = request.form.get(
            "specifications",
            ""
        ).strip()

        price_text = request.form.get(
            "price",
            ""
        ).strip()

        stock_text = request.form.get(
            "stock_quantity",
            ""
        ).strip()

        has_sizes = request.form.get(
            "has_sizes"
        ) == "1"

        featured = request.form.get(
            "featured"
        ) == "1"

        is_active = request.form.get(
            "is_active"
        ) == "1"

        # -------------------------------------------------
        # REQUIRED FIELD VALIDATION
        # -------------------------------------------------

        if not category_id:

            flash(
                "Category is required.",
                "danger"
            )

            return render_template(
                "admin/product_form.html",
                product=None,
                categories=categories,
                subcategories=subcategories,
                brands=brands
            )

        if not sku:

            flash(
                "SKU is required.",
                "danger"
            )

            return render_template(
                "admin/product_form.html",
                product=None,
                categories=categories,
                subcategories=subcategories,
                brands=brands
            )

        if not name:

            flash(
                "Product name is required.",
                "danger"
            )

            return render_template(
                "admin/product_form.html",
                product=None,
                categories=categories,
                subcategories=subcategories,
                brands=brands
            )

        if not price_text:

            flash(
                "Price is required.",
                "danger"
            )

            return render_template(
                "admin/product_form.html",
                product=None,
                categories=categories,
                subcategories=subcategories,
                brands=brands
            )



        # -------------------------------------------------
        # CATEGORY VALIDATION
        # -------------------------------------------------

        try:

            category_id = int(category_id)

        except ValueError:

            flash(
                "Invalid category selected.",
                "danger"
            )

            return render_template(
                "admin/product_form.html",
                product=None,
                categories=categories,
                subcategories=subcategories,
                brands=brands
            )

        category = db.session.get(
            Category,
            category_id
        )

        if not category or not category.is_active:

            flash(
                "Selected category is invalid.",
                "danger"
            )

            return render_template(
                "admin/product_form.html",
                product=None,
                categories=categories,
                subcategories=subcategories,
                brands=brands
            )

        # -------------------------------------------------
        # SUBCATEGORY VALIDATION
        # -------------------------------------------------

        selected_subcategory = None

        if subcategory_id:

            try:

                subcategory_id = int(
                    subcategory_id
                )

            except ValueError:

                flash(
                    "Invalid subcategory selected.",
                    "danger"
                )

                return render_template(
                    "admin/product_form.html",
                    product=None,
                    categories=categories,
                    subcategories=subcategories,
                    brands=brands
                )

            selected_subcategory = db.session.get(
                Subcategory,
                subcategory_id
            )

            if (
                not selected_subcategory
                or not selected_subcategory.is_active
            ):

                flash(
                    "Selected subcategory is invalid.",
                    "danger"
                )

                return render_template(
                    "admin/product_form.html",
                    product=None,
                    categories=categories,
                    subcategories=subcategories,
                    brands=brands
                )

            # Critical consistency check
            if selected_subcategory.category_id != category.id:

                flash(
                    "Selected subcategory does not belong to the selected category.",
                    "danger"
                )

                return render_template(
                    "admin/product_form.html",
                    product=None,
                    categories=categories,
                    subcategories=subcategories,
                    brands=brands
                )

        else:

            subcategory_id = None

        # -------------------------------------------------
        # BRAND VALIDATION
        # -------------------------------------------------

        selected_brand = None

        if brand_id:

            try:

                brand_id = int(
                    brand_id
                )

            except ValueError:

                flash(
                    "Invalid brand selected.",
                    "danger"
                )

                return render_template(
                    "admin/product_form.html",
                    product=None,
                    categories=categories,
                    subcategories=subcategories,
                    brands=brands
                )

            selected_brand = db.session.get(
                Brand,
                brand_id
            )

            if (
                not selected_brand
                or not selected_brand.is_active
            ):

                flash(
                    "Selected brand is invalid.",
                    "danger"
                )

                return render_template(
                    "admin/product_form.html",
                    product=None,
                    categories=categories,
                    subcategories=subcategories,
                    brands=brands
                )

        else:

            brand_id = None

        

        # -------------------------------------------------
        # SKU VALIDATION
        # -------------------------------------------------

        existing_product = Product.query.filter_by(
            sku=sku
        ).first()

        if existing_product:

            flash(
                "A product with this SKU already exists.",
                "danger"
            )

            return render_template(
                "admin/product_form.html",
                product=None,
                categories=categories,
                subcategories=subcategories,
                brands=brands
            )

        # -------------------------------------------------
        # SLUG GENERATION
        # -------------------------------------------------

        base_slug = "-".join(
            name.lower().split()
        )

        slug = base_slug

        counter = 2

        while Product.query.filter_by(
            slug=slug
        ).first():

            slug = f"{base_slug}-{counter}"

            counter += 1

        # -------------------------------------------------
        # PRICE VALIDATION
        # -------------------------------------------------

        try:

            price = float(price_text)

        except ValueError:

            flash(
                "Price must be a valid number.",
                "danger"
            )

            return render_template(
                "admin/product_form.html",
                product=None,
                categories=categories,
                subcategories=subcategories,
                brands=brands
            )

        if price <= 0:

            flash(
                "Price must be greater than 0.",
                "danger"
            )

            return render_template(
                "admin/product_form.html",
                product=None,
                categories=categories,
                subcategories=subcategories,
                brands=brands
            )

        # -------------------------------------------------
        # STOCK / SIZE VALIDATION
        # -------------------------------------------------

        product_sizes = []
        stock_quantity = 0

        if has_sizes:

            try:

                product_sizes, stock_quantity = (
                    get_new_product_sizes_from_form()
                )

            except ValueError as error:

                flash(
                    str(error),
                    "danger"
                )

                return render_template(
                    "admin/product_form.html",
                    product=None,
                    categories=categories,
                    subcategories=subcategories,
                    brands=brands
                )

        else:

            if not stock_text:

                flash(
                    "Stock quantity is required.",
                    "danger"
                )

                return render_template(
                    "admin/product_form.html",
                    product=None,
                    categories=categories,
                    subcategories=subcategories,
                    brands=brands
                )

            try:

                stock_quantity = int(
                    stock_text
                )

            except ValueError:

                flash(
                    "Stock quantity must be a whole number.",
                    "danger"
                )

                return render_template(
                    "admin/product_form.html",
                    product=None,
                    categories=categories,
                    subcategories=subcategories,
                    brands=brands
                )

            if stock_quantity < 0:

                flash(
                    "Stock quantity cannot be negative.",
                    "danger"
                )

                return render_template(
                    "admin/product_form.html",
                    product=None,
                    categories=categories,
                    subcategories=subcategories,
                    brands=brands
                )

        # -------------------------------------------------
        # SPECIFICATIONS JSON
        # -------------------------------------------------

        specifications = None

        if specifications_text:

            import json

            try:

                specifications = json.loads(
                    specifications_text
                )

            except json.JSONDecodeError:

                flash(
                    "Specifications must contain valid JSON.",
                    "danger"
                )

                return render_template(
                    "admin/product_form.html",
                    product=None,
                    categories=categories,
                    subcategories=subcategories,
                    brands=brands
                )

            if not isinstance(
                specifications,
                dict
            ):

                flash(
                    "Specifications must be a JSON object.",
                    "danger"
                )

                return render_template(
                    "admin/product_form.html",
                    product=None,
                    categories=categories,
                    subcategories=subcategories,
                    brands=brands
                )

        # -------------------------------------------------
        # CREATE PRODUCT
        # -------------------------------------------------

        product = Product(
            category_id=category.id,
            subcategory_id=subcategory_id,
            brand_id=brand_id,
            sku=sku,
            name=name,
            slug=slug,
            description=description or None,
            specifications=specifications,
            price=price,
            stock_quantity=stock_quantity,
            featured=featured,
            is_active=is_active
        )

        try:

            db.session.add(product)

            if has_sizes:

                for size_data in product_sizes:

                    product.sizes.append(
                        ProductSize(
                            size=size_data["size"],
                            price=size_data["price"],
                            quantity=size_data["quantity"],
                            description=size_data["description"],
                            specifications=size_data["specifications"]
                        )
                    )

            db.session.commit()

        except IntegrityError:

            db.session.rollback()

            flash(
                "Unable to create product. "
                "Please check the SKU and product details.",
                "danger"
            )

            return render_template(
                "admin/product_form.html",
                product=None,
                categories=categories,
                subcategories=subcategories,
                brands=brands
            )

        flash(
            "Product created successfully.",
            "success"
        )

        return redirect(
            url_for("admin.products")
        )

    return render_template(
        "admin/product_form.html",
        product=None,
        categories=categories,
        subcategories=subcategories,
        brands=brands
    )


# =========================================================
# PRODUCT IMAGE MANAGEMENT
# =========================================================

@admin_bp.route(
    "/products/<int:product_id>/images",
    methods=["GET", "POST"]
)
def product_images(product_id):

    if "admin_id" not in session:
        return redirect(url_for("admin.login"))

    product = db.session.get(
        Product,
        product_id
    )

    if not product:

        flash(
            "Product not found.",
            "danger"
        )

        return redirect(
            url_for("admin.products")
        )

    if request.method == "POST":

        image_files = request.files.getlist(
            "images"
        )

        valid_files = [
            image
            for image in image_files
            if image and image.filename
        ]

        if not valid_files:

            flash(
                "Please select at least one image.",
                "danger"
            )

            return redirect(
                url_for(
                    "admin.product_images",
                    product_id=product.id
                )
            )

        uploaded_images = []

        try:

            existing_images_count = (
                ProductImage.query
                .filter_by(
                    product_id=product.id
                )
                .count()
            )

            for index, image in enumerate(
                valid_files
            ):

                image_key = upload_image(
                    image,
                    "products"
                )

                product_image = ProductImage(
                    product_id=product.id,
                    image_key=image_key,
                    alt_text=product.name,
                    display_order=(
                        existing_images_count + index
                    ),
                    is_primary=(
                        existing_images_count == 0
                        and index == 0
                    )
                )

                db.session.add(
                    product_image
                )

                uploaded_images.append(
                    image_key
                )

            db.session.commit()

        except Exception:

            db.session.rollback()

            # Remove uploaded files if database
            # operation fails.
            for image_key in uploaded_images:

                StorageService().delete(
                    image_key
                )

            flash(
                "Unable to upload product images.",
                "danger"
            )

            return redirect(
                url_for(
                    "admin.product_images",
                    product_id=product.id
                )
            )

        flash(
            f"{len(valid_files)} product image(s) uploaded successfully.",
            "success"
        )

        return redirect(
            url_for(
                "admin.product_images",
                product_id=product.id
            )
        )

    images = (
        ProductImage.query
        .filter_by(
            product_id=product.id
        )
        .order_by(
            ProductImage.display_order.asc(),
            ProductImage.id.asc()
        )
        .all()
    )

    return render_template(
        "admin/product_images.html",
        product=product,
        images=images
    )


# =========================================================
# PRODUCT IMAGE VIEW
# =========================================================

@admin_bp.route(
    "/products/<int:product_id>/images/<int:image_id>/view"
)
def product_image_view(
    product_id,
    image_id
):

    if "admin_id" not in session:
        return redirect(url_for("admin.login"))

    image = (
        ProductImage.query
        .filter_by(
            id=image_id,
            product_id=product_id
        )
        .first()
    )

    if not image:

        return "", 404

    storage = StorageService()

    if not storage.exists(image.image_key):
        return "", 404

    image_file = storage.get_file(
        image.image_key
    )

    from flask import send_file

    return send_file(
        image_file,
        mimetype="image/webp"
    )
# =========================================================
# SET PRIMARY PRODUCT IMAGE
# =========================================================

@admin_bp.route(
    "/products/<int:product_id>/images/<int:image_id>/primary",
    methods=["POST"]
)
def set_primary_product_image(
    product_id,
    image_id
):

    if "admin_id" not in session:
        return redirect(url_for("admin.login"))

    product = db.session.get(
        Product,
        product_id
    )

    if not product:

        flash(
            "Product not found.",
            "danger"
        )

        return redirect(
            url_for("admin.products")
        )

    image = (
        ProductImage.query
        .filter_by(
            id=image_id,
            product_id=product.id
        )
        .first()
    )

    if not image:

        flash(
            "Product image not found.",
            "danger"
        )

        return redirect(
            url_for(
                "admin.product_images",
                product_id=product.id
            )
        )

    try:

        # Remove primary status from all
        # images belonging to this product.
        (
            ProductImage.query
            .filter_by(
                product_id=product.id
            )
            .update(
                {
                    ProductImage.is_primary: False
                },
                synchronize_session=False
            )
        )

        # Set selected image as primary.
        image.is_primary = True

        db.session.commit()

    except Exception:

        db.session.rollback()

        flash(
            "Unable to set primary image.",
            "danger"
        )

        return redirect(
            url_for(
                "admin.product_images",
                product_id=product.id
            )
        )

    flash(
        "Primary product image updated successfully.",
        "success"
    )

    return redirect(
        url_for(
            "admin.product_images",
            product_id=product.id
        )
    )


# =========================================================
# DELETE PRODUCT IMAGE
# =========================================================

@admin_bp.route(
    "/products/<int:product_id>/images/<int:image_id>/delete",
    methods=["POST"]
)
def delete_product_image(
    product_id,
    image_id
):

    if "admin_id" not in session:
        return redirect(url_for("admin.login"))

    product = db.session.get(
        Product,
        product_id
    )

    if not product:

        flash(
            "Product not found.",
            "danger"
        )

        return redirect(
            url_for("admin.products")
        )

    image = (
        ProductImage.query
        .filter_by(
            id=image_id,
            product_id=product.id
        )
        .first()
    )

    if not image:

        flash(
            "Product image not found.",
            "danger"
        )

        return redirect(
            url_for(
                "admin.product_images",
                product_id=product.id
            )
        )

    image_key = image.image_key
    was_primary = image.is_primary

    try:

        db.session.delete(image)
        db.session.commit()

    except Exception:

        db.session.rollback()

        flash(
            "Unable to delete product image.",
            "danger"
        )

        return redirect(
            url_for(
                "admin.product_images",
                product_id=product.id
            )
        )

    # Delete physical image only after
    # successful database deletion.
    if image_key:

        StorageService().delete(
            image_key
        )

    # If the deleted image was primary,
    # automatically make the first remaining
    # image primary.
    if was_primary:

        remaining_image = (
            ProductImage.query
            .filter_by(
                product_id=product.id
            )
            .order_by(
                ProductImage.display_order.asc(),
                ProductImage.id.asc()
            )
            .first()
        )

        if remaining_image:

            remaining_image.is_primary = True

            db.session.commit()

    flash(
        "Product image permanently deleted.",
        "success"
    )

    return redirect(
        url_for(
            "admin.product_images",
            product_id=product.id
        )
    )


# =========================================================
# UPDATE PRODUCT IMAGE ORDER
# =========================================================

@admin_bp.route(
    "/products/<int:product_id>/images/order",
    methods=["POST"]
)
def update_product_image_order(product_id):

    if "admin_id" not in session:
        return redirect(url_for("admin.login"))

    product = db.session.get(
        Product,
        product_id
    )

    if not product:

        flash(
            "Product not found.",
            "danger"
        )

        return redirect(
            url_for("admin.products")
        )

    images = (
        ProductImage.query
        .filter_by(
            product_id=product.id
        )
        .all()
    )

    try:

        for image in images:

            order_value = request.form.get(
                f"display_order_{image.id}",
                ""
            ).strip()

            if not order_value:

                raise ValueError(
                    "Display order cannot be empty."
                )

            order_value = int(
                order_value
            )

            if order_value < 0:

                raise ValueError(
                    "Display order cannot be negative."
                )

            image.display_order = order_value

        db.session.commit()

    except (ValueError, TypeError):

        db.session.rollback()

        flash(
            "Display order must contain valid non-negative numbers.",
            "danger"
        )

        return redirect(
            url_for(
                "admin.product_images",
                product_id=product.id
            )
        )

    except Exception:

        db.session.rollback()

        flash(
            "Unable to update image order.",
            "danger"
        )

        return redirect(
            url_for(
                "admin.product_images",
                product_id=product.id
            )
        )

    flash(
        "Product image order updated successfully.",
        "success"
    )

    return redirect(
        url_for(
            "admin.product_images",
            product_id=product.id
        )
    )


# =========================================================
# EDIT PRODUCT
# =========================================================

@admin_bp.route(
    "/products/<int:product_id>/edit",
    methods=["GET", "POST"]
)
def edit_product(product_id):

    if "admin_id" not in session:
        return redirect(url_for("admin.login"))

    product = db.session.get(
        Product,
        product_id
    )

    if not product:

        flash(
            "Product not found.",
            "danger"
        )

        return redirect(
            url_for("admin.products")
        )

    categories = (
        Category.query
        .filter_by(is_active=True)
        .order_by(Category.name.asc())
        .all()
    )

    subcategories = (
        Subcategory.query
        .filter_by(is_active=True)
        .order_by(Subcategory.name.asc())
        .all()
    )

    brands = (
        Brand.query
        .filter_by(is_active=True)
        .order_by(Brand.name.asc())
        .all()
    )

    if request.method == "POST":

        category_id = request.form.get(
            "category_id",
            ""
        ).strip()

        subcategory_id = request.form.get(
            "subcategory_id",
            ""
        ).strip()

        brand_id = request.form.get(
            "brand_id",
            ""
        ).strip()

        sku = request.form.get(
            "sku",
            ""
        ).strip().upper()

        name = request.form.get(
            "name",
            ""
        ).strip()

        description = request.form.get(
            "description",
            ""
        ).strip()

        specifications_text = request.form.get(
            "specifications",
            ""
        ).strip()

        price_text = request.form.get(
            "price",
            ""
        ).strip()

        stock_text = request.form.get(
            "stock_quantity",
            ""
        ).strip()

        has_sizes = request.form.get(
            "has_sizes"
        ) == "1"

        featured = request.form.get(
            "featured"
        ) == "1"

        is_active = request.form.get(
            "is_active"
        ) == "1"

        # -------------------------------------------------
        # REQUIRED FIELDS
        # -------------------------------------------------

        if not category_id:

            flash(
                "Category is required.",
                "danger"
            )

            return render_template(
                "admin/product_form.html",
                product=product,
                categories=categories,
                subcategories=subcategories,
                brands=brands
            )

        if not sku:

            flash(
                "SKU is required.",
                "danger"
            )

            return render_template(
                "admin/product_form.html",
                product=product,
                categories=categories,
                subcategories=subcategories,
                brands=brands
            )

        if not name:

            flash(
                "Product name is required.",
                "danger"
            )

            return render_template(
                "admin/product_form.html",
                product=product,
                categories=categories,
                subcategories=subcategories,
                brands=brands
            )

        if not price_text:

            flash(
                "Price is required.",
                "danger"
            )

            return render_template(
                "admin/product_form.html",
                product=product,
                categories=categories,
                subcategories=subcategories,
                brands=brands
            )



        # -------------------------------------------------
        # CATEGORY
        # -------------------------------------------------

        try:

            category_id = int(category_id)

        except ValueError:

            flash(
                "Invalid category selected.",
                "danger"
            )

            return render_template(
                "admin/product_form.html",
                product=product,
                categories=categories,
                subcategories=subcategories,
                brands=brands
            )

        category = db.session.get(
            Category,
            category_id
        )

        if not category or not category.is_active:

            flash(
                "Selected category is invalid.",
                "danger"
            )

            return render_template(
                "admin/product_form.html",
                product=product,
                categories=categories,
                subcategories=subcategories,
                brands=brands
            )

        # -------------------------------------------------
        # SUBCATEGORY
        # -------------------------------------------------

        selected_subcategory = None

        if subcategory_id:

            try:

                subcategory_id = int(
                    subcategory_id
                )

            except ValueError:

                flash(
                    "Invalid subcategory selected.",
                    "danger"
                )

                return render_template(
                    "admin/product_form.html",
                    product=product,
                    categories=categories,
                    subcategories=subcategories,
                    brands=brands
                )

            selected_subcategory = db.session.get(
                Subcategory,
                subcategory_id
            )

            if (
                not selected_subcategory
                or not selected_subcategory.is_active
            ):

                flash(
                    "Selected subcategory is invalid.",
                    "danger"
                )

                return render_template(
                    "admin/product_form.html",
                    product=product,
                    categories=categories,
                    subcategories=subcategories,
                    brands=brands
                )

            if selected_subcategory.category_id != category.id:

                flash(
                    "Selected subcategory does not belong to the selected category.",
                    "danger"
                )

                return render_template(
                    "admin/product_form.html",
                    product=product,
                    categories=categories,
                    subcategories=subcategories,
                    brands=brands
                )

        else:

            subcategory_id = None

        # -------------------------------------------------
        # BRAND
        # -------------------------------------------------

        selected_brand = None

        if brand_id:

            try:

                brand_id = int(brand_id)

            except ValueError:

                flash(
                    "Invalid brand selected.",
                    "danger"
                )

                return render_template(
                    "admin/product_form.html",
                    product=product,
                    categories=categories,
                    subcategories=subcategories,
                    brands=brands
                )

            selected_brand = db.session.get(
                Brand,
                brand_id
            )

            if (
                not selected_brand
                or not selected_brand.is_active
            ):

                flash(
                    "Selected brand is invalid.",
                    "danger"
                )

                return render_template(
                    "admin/product_form.html",
                    product=product,
                    categories=categories,
                    subcategories=subcategories,
                    brands=brands
                )

        else:

            brand_id = None

        # -------------------------------------------------
        # SKU
        # -------------------------------------------------

        existing_product = (
            Product.query
            .filter(
                Product.sku == sku,
                Product.id != product.id
            )
            .first()
        )

        if existing_product:

            flash(
                "Another product with this SKU already exists.",
                "danger"
            )

            return render_template(
                "admin/product_form.html",
                product=product,
                categories=categories,
                subcategories=subcategories,
                brands=brands
            )

        # -------------------------------------------------
        # SLUG
        # -------------------------------------------------

        base_slug = "-".join(
            name.lower().split()
        )

        slug = base_slug

        counter = 2

        while True:

            existing_slug = (
                Product.query
                .filter(
                    Product.slug == slug,
                    Product.id != product.id
                )
                .first()
            )

            if not existing_slug:
                break

            slug = f"{base_slug}-{counter}"

            counter += 1

        # -------------------------------------------------
        # PRICE
        # -------------------------------------------------

        try:

            price = float(price_text)

        except ValueError:

            flash(
                "Price must be a valid number.",
                "danger"
            )

            return render_template(
                "admin/product_form.html",
                product=product,
                categories=categories,
                subcategories=subcategories,
                brands=brands
            )

        if price <= 0:

            flash(
                "Price must be greater than 0.",
                "danger"
            )

            return render_template(
                "admin/product_form.html",
                product=product,
                categories=categories,
                subcategories=subcategories,
                brands=brands
            )

        # -------------------------------------------------
        # STOCK / SIZE VALIDATION
        # -------------------------------------------------

        product_sizes = []
        stock_quantity = 0

        if has_sizes:

            try:

                product_sizes, stock_quantity = (
                    get_product_sizes_from_form()
                )

            except ValueError as error:

                flash(
                    str(error),
                    "danger"
                )

                return render_template(
                    "admin/product_form.html",
                    product=product,
                    categories=categories,
                    subcategories=subcategories,
                    brands=brands
                )

        else:

            if not stock_text:

                flash(
                    "Stock quantity is required.",
                    "danger"
                )

                return render_template(
                    "admin/product_form.html",
                    product=product,
                    categories=categories,
                    subcategories=subcategories,
                    brands=brands
                )

            try:

                stock_quantity = int(
                    stock_text
                )

            except ValueError:

                flash(
                    "Stock quantity must be a whole number.",
                    "danger"
                )

                return render_template(
                    "admin/product_form.html",
                    product=product,
                    categories=categories,
                    subcategories=subcategories,
                    brands=brands
                )

            if stock_quantity < 0:

                flash(
                    "Stock quantity cannot be negative.",
                    "danger"
                )

                return render_template(
                    "admin/product_form.html",
                    product=product,
                    categories=categories,
                    subcategories=subcategories,
                    brands=brands
                )
        # -------------------------------------------------
        # SPECIFICATIONS
        # -------------------------------------------------

        specifications = None

        if specifications_text:

            import json

            try:

                specifications = json.loads(
                    specifications_text
                )

            except json.JSONDecodeError:

                flash(
                    "Specifications must contain valid JSON.",
                    "danger"
                )

                return render_template(
                    "admin/product_form.html",
                    product=product,
                    categories=categories,
                    subcategories=subcategories,
                    brands=brands
                )

            if not isinstance(
                specifications,
                dict
            ):

                flash(
                    "Specifications must be a JSON object.",
                    "danger"
                )

                return render_template(
                    "admin/product_form.html",
                    product=product,
                    categories=categories,
                    subcategories=subcategories,
                    brands=brands
                )

        # -------------------------------------------------
        # UPDATE PRODUCT
        # -------------------------------------------------

        product.category_id = category.id
        product.subcategory_id = subcategory_id
        product.brand_id = brand_id
        product.sku = sku
        product.name = name
        product.slug = slug
        product.description = description or None
        product.specifications = specifications
        product.price = price
        product.stock_quantity = stock_quantity
        product.featured = featured
        product.is_active = is_active

        try:

            if has_sizes:

                # -------------------------------------------------
                # UPDATE EXISTING VARIANTS / CREATE NEW VARIANTS
                #
                # Existing ProductSize IDs are preserved.
                # This is important because CartItem.product_size_id
                # references ProductSize.id.
                # -------------------------------------------------

                existing_variants = {
                    item.id: item
                    for item in product.sizes
                }

                submitted_variant_ids = set()

                protected_variants = []


                for size_data in product_sizes:

                    product_size_id = (
                        size_data["product_size_id"]
                    )


                    # -------------------------------------------------
                    # EXISTING VARIANT
                    # -------------------------------------------------

                    if product_size_id is not None:

                        existing_variant = (
                            existing_variants.get(
                                product_size_id
                            )
                        )


                        # -------------------------------------------------
                        # INVALID VARIANT ID
                        # -------------------------------------------------

                        if not existing_variant:

                            db.session.rollback()

                            flash(
                                "Invalid product variant selected.",
                                "danger"
                            )

                            return render_template(
                                "admin/product_form.html",
                                product=product,
                                categories=categories,
                                subcategories=subcategories,
                                brands=brands
                            )


                        submitted_variant_ids.add(
                            existing_variant.id
                        )


                        # -------------------------------------------------
                        # UPDATE SAME PRODUCT SIZE RECORD
                        # -------------------------------------------------

                        existing_variant.size = (
                            size_data["size"]
                        )

                        existing_variant.price = (
                            size_data["price"]
                        )

                        existing_variant.quantity = (
                            size_data["quantity"]
                        )

                        existing_variant.description = (
                            size_data["description"]
                        )

                        existing_variant.specifications = (
                            size_data["specifications"]
                        )


                    # -------------------------------------------------
                    # NEW VARIANT
                    # -------------------------------------------------

                    else:

                        product.sizes.append(
                            ProductSize(
                                size=size_data["size"],
                                price=size_data["price"],
                                quantity=size_data["quantity"],
                                description=size_data["description"],
                                specifications=size_data["specifications"]
                            )
                        )


                # -------------------------------------------------
                # HANDLE REMOVED VARIANTS
                # -------------------------------------------------
                #
                # Any existing variant that was not submitted
                # has been removed from the Admin form.
                #
                # If it is currently used by a CartItem, do NOT
                # delete it because cart_items.product_size_id
                # uses ON DELETE CASCADE.
                # -------------------------------------------------

                for existing_variant in product.sizes:

                    if existing_variant.id in submitted_variant_ids:

                        continue


                    # Newly-created variants do not have an ID
                    # until the session is flushed.
                    if existing_variant.id is None:

                        continue


                    cart_usage_count = db.session.execute(
                        db.text(
                            """
                            SELECT COUNT(*)
                            FROM cart_items
                            WHERE product_size_id = :product_size_id
                            """
                        ),
                        {
                            "product_size_id":
                                existing_variant.id
                        }
                    ).scalar()


                    if cart_usage_count and cart_usage_count > 0:

                        protected_variants.append(
                            existing_variant.size
                        )

                    else:

                        db.session.delete(
                            existing_variant
                        )


                # -------------------------------------------------
                # BLOCK REMOVAL OF CART-USED VARIANTS
                # -------------------------------------------------

                if protected_variants:

                    db.session.rollback()

                    protected_names = ", ".join(
                        protected_variants
                    )

                    flash(
                        "The following variant(s) cannot be "
                        "removed because they are currently "
                        f"in customer carts: {protected_names}",
                        "warning"
                    )

                    return render_template(
                        "admin/product_form.html",
                        product=product,
                        categories=categories,
                        subcategories=subcategories,
                        brands=brands
                    )
            else:

                # Product no longer uses sizes.
                product.sizes.clear()

            db.session.commit()

        except IntegrityError as error:

            db.session.rollback()

            print(
                "PRODUCT UPDATE INTEGRITY ERROR:",
                error
            )

            flash(
                "Unable to update product. "
                "Please check the product details.",
                "danger"
            )

            return render_template(
                "admin/product_form.html",
                product=product,
                categories=categories,
                subcategories=subcategories,
                brands=brands
            )
        return redirect(
            url_for("admin.products")
        )

    return render_template(
        "admin/product_form.html",
        product=product,
        categories=categories,
        subcategories=subcategories,
        brands=brands
    )


# =========================================================
# DELETE PRODUCT
# =========================================================

@admin_bp.route(
    "/products/<int:product_id>/delete",
    methods=["POST"]
)
def delete_product(product_id):

    if "admin_id" not in session:
        return redirect(url_for("admin.login"))

    product = db.session.get(
        Product,
        product_id
    )

    if not product:

        flash(
            "Product not found.",
            "danger"
        )

        return redirect(
            url_for("admin.products")
        )

    # -----------------------------------------------------
    # ORDER DEPENDENCY CHECK
    # -----------------------------------------------------
    #
    # A product that has appeared in an order must not
    # be permanently deleted. The order_items table keeps
    # the product reference as NULL after deletion, but
    # preserves the historical product name, SKU and price.
    #
    # We therefore block deletion when order history exists.
    # -----------------------------------------------------

    order_item_count = db.session.execute(
        db.text(
            """
            SELECT COUNT(*)
            FROM order_items
            WHERE product_id = :product_id
            """
        ),
        {
            "product_id": product.id
        }
    ).scalar()

    if order_item_count and order_item_count > 0:

        flash(
            "Product cannot be permanently deleted because "
            "it is associated with existing order history.",
            "danger"
        )

        return redirect(
            url_for("admin.products")
        )

    # -----------------------------------------------------
    # SAVE IMAGE KEYS BEFORE DATABASE DELETE
    # -----------------------------------------------------
    #
    # product_images are removed automatically by the
    # database because of ON DELETE CASCADE.
    #
    # We must therefore collect their physical image keys
    # before deleting the product.
    # -----------------------------------------------------

    product_images = (
        ProductImage.query
        .filter_by(
            product_id=product.id
        )
        .all()
    )

    image_keys = [
        image.image_key
        for image in product_images
        if image.image_key
    ]

    # -----------------------------------------------------
    # DELETE PRODUCT
    # -----------------------------------------------------

    try:

        db.session.delete(product)
        db.session.commit()

    except Exception:

        db.session.rollback()

        flash(
            "Product could not be deleted.",
            "danger"
        )

        return redirect(
            url_for("admin.products")
        )

    # -----------------------------------------------------
    # DELETE PHYSICAL IMAGE FILES
    # -----------------------------------------------------
    #
    # Database deletion succeeded first.
    # Only now remove the stored image files.
    # -----------------------------------------------------

    failed_image_deletes = []

    storage = StorageService()

    for image_key in image_keys:

        try:

            deleted = storage.delete(
                image_key
            )

            if not deleted:

                failed_image_deletes.append(
                    image_key
                )

        except Exception:

            failed_image_deletes.append(
                image_key
            )

    # -----------------------------------------------------
    # RESULT MESSAGE
    # -----------------------------------------------------

    if failed_image_deletes:

        flash(
            "Product was deleted successfully, but some "
            "product image files could not be removed.",
            "warning"
        )

    else:

        flash(
            "Product permanently deleted.",
            "success"
        )

    return redirect(
        url_for("admin.products")
    )


# =========================================================
# USERS MANAGEMENT
# =========================================================

@admin_bp.route("/users")
def users():

    if "admin_id" not in session:
        return redirect(url_for("admin.login"))

    # -----------------------------------------------------
    # GET USERS WITH ORDER COUNT
    # -----------------------------------------------------

    results = (
        db.session.query(
            User,
            func.count(Order.id).label(
                "order_count"
            )
        )
        .outerjoin(
            Order,
            User.id == Order.user_id
        )
        .group_by(
            User.id
        )
        .order_by(
            User.created_at.desc()
        )
        .all()
    )


    # -----------------------------------------------------
    # PREPARE USER DATA FOR TEMPLATE
    # -----------------------------------------------------

    users = []

    for user, order_count in results:

        users.append(
            {
                "user": user,
                "order_count": order_count
            }
        )


    return render_template(
        "admin/users.html",
        users=users
    )

# =========================================================
# USER DETAILS
# =========================================================

@admin_bp.route(
    "/users/<int:user_id>"
)
def user_details(user_id):

    if "admin_id" not in session:
        return redirect(url_for("admin.login"))

    # -----------------------------------------------------
    # GET USER
    # -----------------------------------------------------

    user = db.session.get(
        User,
        user_id
    )

    if not user:

        flash(
            "User not found.",
            "danger"
        )

        return redirect(
            url_for("admin.users")
        )

    # -----------------------------------------------------
    # GET ALL ORDERS OF THIS USER
    # -----------------------------------------------------

    orders = (
        Order.query
        .filter(
            Order.user_id == user.id
        )
        .order_by(
            Order.created_at.desc()
        )
        .all()
    )

    # -----------------------------------------------------
    # GET ITEMS + PRODUCT IMAGES FOR EACH ORDER
    # -----------------------------------------------------

    order_items = {}
    order_item_images = {}

    for order in orders:

        items = (
            OrderItem.query
            .filter(
                OrderItem.order_id == order.id
            )
            .order_by(
                OrderItem.id.asc()
            )
            .all()
        )

        order_items[order.id] = items

        # ---------------------------------------------
        # FIND PRODUCT IMAGE FOR EACH ORDER ITEM
        # ---------------------------------------------

        for item in items:

            if not item.product_id:
                continue

            image = (
                ProductImage.query
                .filter(
                    ProductImage.product_id == item.product_id
                )
                .order_by(
                    ProductImage.is_primary.desc(),
                    ProductImage.display_order.asc(),
                    ProductImage.id.asc()
                )
                .first()
            )

            order_item_images[item.id] = image

    # -----------------------------------------------------
    # RENDER ONE COMPLETE USER PAGE
    # -----------------------------------------------------

    return render_template(
        "admin/user_details.html",
        user=user,
        orders=orders,
        order_items=order_items,
        order_item_images=order_item_images
    )

# =========================================================
# TOGGLE USER ACCOUNT STATUS
# =========================================================

@admin_bp.route(
    "/users/<int:user_id>/toggle",
    methods=["POST"]
)
def toggle_user(user_id):

    if "admin_id" not in session:
        return redirect(url_for("admin.login"))

    user = db.session.get(
        User,
        user_id
    )

    if not user:

        flash(
            "User not found.",
            "danger"
        )

        return redirect(
            url_for("admin.users")
        )

    # Toggle account status
    user.is_active = not user.is_active

    try:

        db.session.commit()

    except Exception:

        db.session.rollback()

        flash(
            "Unable to update user account status.",
            "danger"
        )

        return redirect(
            url_for(
                "admin.user_details",
                user_id=user.id
            )
        )

    if user.is_active:

        flash(
            f"{user.full_name} has been activated.",
            "success"
        )

    else:

        flash(
            f"{user.full_name} has been deactivated.",
            "success"
        )

    return redirect(
        url_for(
            "admin.user_details",
            user_id=user.id
        )
    )

# =========================================================
# ORDER MANAGEMENT
# =========================================================

@admin_bp.route("/orders")
def orders():

    if "admin_id" not in session:
        return redirect(
            url_for("admin.login")
        )

    # -----------------------------------------------------
    # SEARCH
    # -----------------------------------------------------

    search = request.args.get(
        "search",
        ""
    ).strip()


    # -----------------------------------------------------
    # STATUS FILTER
    # -----------------------------------------------------

    status = request.args.get(
        "status",
        ""
    ).strip().upper()


    # -----------------------------------------------------
    # BASE QUERY
    # -----------------------------------------------------

    query = (
        Order.query
        .join(
            User,
            Order.user_id == User.id
        )
    )


    # -----------------------------------------------------
    # SEARCH
    #
    # Order number
    # Customer name
    # Email
    # Phone
    # -----------------------------------------------------

    if search:

        search_pattern = (
            f"%{search}%"
        )

        query = query.filter(
            db.or_(
                Order.order_number.ilike(
                    search_pattern
                ),

                User.full_name.ilike(
                    search_pattern
                ),

                User.email.ilike(
                    search_pattern
                ),

                User.phone.ilike(
                    search_pattern
                )
            )
        )


    # -----------------------------------------------------
    # STATUS FILTER
    # -----------------------------------------------------

    allowed_statuses = {
        "PENDING",
        "CONFIRMED",
        "SHIPPED",
        "DELIVERED"
    }


    if status in allowed_statuses:

        query = query.filter(
            Order.status == status
        )

    else:

        status = ""


    # -----------------------------------------------------
    # GET ORDERS
    # -----------------------------------------------------

    orders = (
        query
        .order_by(
            Order.created_at.desc()
        )
        .all()
    )


    return render_template(
        "admin/orders.html",
        orders=orders,
        search=search,
        status=status
    )

# =========================================================
# REVENUE MANAGEMENT
# =========================================================

@admin_bp.route("/revenue")
def revenue():

    if "admin_id" not in session:
        return redirect(
            url_for("admin.login")
        )

    from datetime import datetime

    # -----------------------------------------------------
    # SELECTED REVENUE SECTION
    # -----------------------------------------------------
    #
    # overview     -> overall revenue + graph
    # category     -> category-wise revenue
    # subcategory  -> subcategory-wise revenue
    #
    # The Revenue page will display only one section
    # at a time.
    # -----------------------------------------------------

    section = request.args.get(
        "section",
        "overview"
    ).strip().lower()

    allowed_sections = {
        "overview",
        "category",
        "subcategory"
    }

    if section not in allowed_sections:
        section = "overview"

    # -----------------------------------------------------
    # ONLY DELIVERED ORDERS COUNT AS REVENUE
    # -----------------------------------------------------

    delivered_orders = (
        Order.query
        .filter(
            Order.status == "DELIVERED"
        )
        .order_by(
            Order.created_at.asc()
        )
        .all()
    )

    # -----------------------------------------------------
    # BASIC REVENUE TOTAL
    # -----------------------------------------------------

    total_revenue = sum(
        float(order.total_amount or 0)
        for order in delivered_orders
    )

    # -----------------------------------------------------
    # TODAY
    # -----------------------------------------------------

    today = datetime.now().date()

    today_revenue = sum(
        float(order.total_amount or 0)
        for order in delivered_orders
        if (
            order.created_at
            and order.created_at.date() == today
        )
    )

    # -----------------------------------------------------
    # CURRENT MONTH
    # -----------------------------------------------------

    current_year = today.year
    current_month = today.month

    monthly_revenue_value = sum(
        float(order.total_amount or 0)
        for order in delivered_orders
        if (
            order.created_at
            and order.created_at.year == current_year
            and order.created_at.month == current_month
        )
    )

    # -----------------------------------------------------
    # CURRENT QUARTER
    # -----------------------------------------------------

    current_quarter = (
        (today.month - 1) // 3
    ) + 1

    quarter_start_month = (
        (current_quarter - 1) * 3
    ) + 1

    quarter_revenue = sum(
        float(order.total_amount or 0)
        for order in delivered_orders
        if (
            order.created_at
            and order.created_at.year == current_year
            and quarter_start_month
            <= order.created_at.month
            <= quarter_start_month + 2
        )
    )

    # -----------------------------------------------------
    # DAILY REVENUE
    # -----------------------------------------------------

    daily_data = {}

    for order in delivered_orders:

        if not order.created_at:
            continue

        date_key = (
            order.created_at.date()
        )

        if date_key not in daily_data:

            daily_data[date_key] = {
                "label": order.created_at.strftime(
                    "%d %b"
                ),
                "revenue": 0
            }

        daily_data[date_key]["revenue"] += (
            float(order.total_amount or 0)
        )

    daily_revenue = [
        {
            "label": data["label"],
            "revenue": round(
                data["revenue"],
                2
            )
        }
        for key, data in sorted(
            daily_data.items()
        )
    ]

    # Latest 14 revenue days
    daily_revenue = daily_revenue[-14:]

    # -----------------------------------------------------
    # MONTHLY REVENUE
    # -----------------------------------------------------

    monthly_data = {}

    for order in delivered_orders:

        if not order.created_at:
            continue

        month_key = (
            order.created_at.strftime(
                "%Y-%m"
            )
        )

        if month_key not in monthly_data:

            monthly_data[month_key] = {
                "label": order.created_at.strftime(
                    "%b %Y"
                ),
                "revenue": 0
            }

        monthly_data[month_key]["revenue"] += (
            float(order.total_amount or 0)
        )

    monthly_revenue = [
        {
            "label": data["label"],
            "revenue": round(
                data["revenue"],
                2
            )
        }
        for key, data in sorted(
            monthly_data.items()
        )
    ]

    # Latest 12 months
    monthly_revenue = monthly_revenue[-12:]

    # -----------------------------------------------------
    # QUARTERLY REVENUE
    # -----------------------------------------------------

    quarterly_data = {}

    for order in delivered_orders:

        if not order.created_at:
            continue

        order_year = order.created_at.year

        order_quarter = (
            (order.created_at.month - 1) // 3
        ) + 1

        quarter_key = (
            order_year,
            order_quarter
        )

        if quarter_key not in quarterly_data:

            quarterly_data[quarter_key] = {
                "label": (
                    f"Q{order_quarter} "
                    f"{order_year}"
                ),
                "revenue": 0
            }

        quarterly_data[quarter_key]["revenue"] += (
            float(order.total_amount or 0)
        )

    quarterly_revenue = [
        {
            "label": data["label"],
            "revenue": round(
                data["revenue"],
                2
            )
        }
        for key, data in sorted(
            quarterly_data.items()
        )
    ]

    # Latest 8 quarters
    quarterly_revenue = quarterly_revenue[-8:]

    # -----------------------------------------------------
    # CATEGORY REVENUE
    # -----------------------------------------------------

    category_data = {}

    for order in delivered_orders:

        for item in order.items:

            product = item.product

            if not product:
                continue

            category = product.category

            if not category:
                continue

            category_id = category.id

            if category_id not in category_data:

                category_data[category_id] = {
                    "id": category.id,
                    "name": category.name,
                    "image_url": url_for(
                        "admin.category_image",
                        category_id=category.id
                    )
                    if category.image_key
                    else None,
                    "revenue": 0,
                    "items": 0
                }

            category_data[category_id]["revenue"] += (
                float(item.total_price or 0)
            )

            category_data[category_id]["items"] += (
                int(item.quantity or 0)
            )

    category_revenue = sorted(
        category_data.values(),
        key=lambda item: item["revenue"],
        reverse=True
    )

    for category in category_revenue:

        category["revenue"] = round(
            category["revenue"],
            2
        )

    # -----------------------------------------------------
    # SUBCATEGORY REVENUE
    # -----------------------------------------------------
    #
    # All subcategories are kept in ONE ranking.
    #
    # They are NOT grouped under categories.
    #
    # Each row contains:
    # - image
    # - subcategory
    # - parent category
    # - revenue
    # - quantity sold
    # - most sold product
    # -----------------------------------------------------

    subcategory_data = {}

    for order in delivered_orders:

        for item in order.items:

            product = item.product

            if not product:
                continue

            subcategory = (
                product.subcategory
            )

            if not subcategory:
                continue

            subcategory_id = (
                subcategory.id
            )

            if (
                subcategory_id
                not in subcategory_data
            ):

                parent_category = (
                    subcategory.category
                )

                subcategory_data[
                    subcategory_id
                ] = {
                    "id": subcategory.id,
                    "name": subcategory.name,
                    "image_url": url_for(
                        "admin.subcategory_image",
                        subcategory_id=subcategory.id
                    )
                    if subcategory.image_key
                    else None,
                    "category_name": (
                        parent_category.name
                        if parent_category
                        else "—"
                    ),
                    "revenue": 0,
                    "items": 0,
                    "products": {}
                }

            subcategory_data[
                subcategory_id
            ]["revenue"] += (
                float(item.total_price or 0)
            )

            subcategory_data[
                subcategory_id
            ]["items"] += (
                int(item.quantity or 0)
            )

            # -------------------------------------------------
            # MOST SOLD PRODUCT
            # -------------------------------------------------

            product_id = (
                product.id
            )

            if (
                product_id
                not in subcategory_data[
                    subcategory_id
                ]["products"]
            ):

                image = (
                    ProductImage.query
                    .filter(
                        ProductImage.product_id
                        == product.id
                    )
                    .order_by(
                        ProductImage.is_primary.desc(),
                        ProductImage.display_order.asc(),
                        ProductImage.id.asc()
                    )
                    .first()
                )

                subcategory_data[
                    subcategory_id
                ]["products"][product_id] = {
                    "id": product.id,
                    "name": (
                        item.product_name
                        or product.name
                    ),
                    "quantity": 0,
                    "image_url": (
                        url_for(
                            "admin.product_image_view",
                            product_id=product.id,
                            image_id=image.id
                        )
                        + f"?v={image.id}"
                    )
                    if image
                    else None
                }

            subcategory_data[
                subcategory_id
            ]["products"][
                product_id
            ]["quantity"] += (
                int(item.quantity or 0)
            )

    # -----------------------------------------------------
    # PREPARE SUBCATEGORY LIST
    # -----------------------------------------------------

    subcategory_revenue = []

    for data in subcategory_data.values():

        products = list(
            data["products"].values()
        )

        products.sort(
            key=lambda product: product["quantity"],
            reverse=True
        )

        most_sold_product = (
            products[0]
            if products
            else None
        )

        subcategory_revenue.append(
            {
                "id": data["id"],
                "name": data["name"],
                "image_url": data["image_url"],
                "category_name": data[
                    "category_name"
                ],
                "revenue": round(
                    data["revenue"],
                    2
                ),
                "items": data["items"],
                "most_sold_product": (
                    most_sold_product
                )
            }
        )

    subcategory_revenue.sort(
        key=lambda item: item["revenue"],
        reverse=True
    )

    # -----------------------------------------------------
    # SUBCATEGORY GRAPH DATA
    # -----------------------------------------------------

    subcategory_graph = [
        {
            "label": item["name"],
            "revenue": item["revenue"]
        }
        for item in subcategory_revenue
    ]

    # -----------------------------------------------------
    # CATEGORY GRAPH DATA
    # -----------------------------------------------------

    category_graph = [
        {
            "label": item["name"],
            "revenue": item["revenue"]
        }
        for item in category_revenue
    ]

    # -----------------------------------------------------
    # RENDER REVENUE PAGE
    # -----------------------------------------------------

    return render_template(
        "admin/revenue.html",

        section=section,

        total_revenue=round(
            total_revenue,
            2
        ),

        today_revenue=round(
            today_revenue,
            2
        ),

        monthly_revenue_value=round(
            monthly_revenue_value,
            2
        ),

        quarter_revenue=round(
            quarter_revenue,
            2
        ),

        daily_revenue=daily_revenue,

        monthly_revenue=monthly_revenue,

        quarterly_revenue=quarterly_revenue,

        category_revenue=category_revenue,

        category_graph=category_graph,

        subcategory_revenue=subcategory_revenue,

        subcategory_graph=subcategory_graph
    )

# =========================================================
# TRAFFIC MANAGEMENT
# =========================================================

@admin_bp.route("/traffic")
def traffic():

    if "admin_id" not in session:
        return redirect(
            url_for("admin.login")
        )

    from datetime import datetime
    from collections import defaultdict


    # -----------------------------------------------------
    # GET ALL TRAFFIC EVENTS
    # -----------------------------------------------------

    events = (
        TrafficEvent.query
        .order_by(
            TrafficEvent.created_at.asc()
        )
        .all()
    )


    # -----------------------------------------------------
    # BASIC VISITOR / SESSION STATISTICS
    # -----------------------------------------------------

    visitor_users = defaultdict(set)

    session_users = defaultdict(set)

    session_times = defaultdict(list)


    for event in events:

        if not event.visitor_id:
            continue

        if event.user_id:

            visitor_users[
                event.visitor_id
            ].add(
                event.user_id
            )

        if event.session_id:

            if event.user_id:

                session_users[
                    event.session_id
                ].add(
                    event.user_id
                )

            if event.created_at:

                session_times[
                    event.session_id
                ].append(
                    event.created_at
                )


    # -----------------------------------------------------
    # TOTAL VISITORS
    # -----------------------------------------------------

    total_visitors = len(
        {
            event.visitor_id
            for event in events
            if event.visitor_id
        }
    )


    # -----------------------------------------------------
    # LOGGED-IN / GUEST VISITORS
    # -----------------------------------------------------

    logged_in_visitors = len(
        {
            visitor_id
            for visitor_id, users
            in visitor_users.items()
            if users
        }
    )


    guest_visitors = max(
        total_visitors - logged_in_visitors,
        0
    )


    # -----------------------------------------------------
    # TOTAL SESSIONS
    # -----------------------------------------------------

    total_sessions = len(
        {
            event.session_id
            for event in events
            if event.session_id
        }
    )


    # =====================================================
    # SESSION DURATION
    # =====================================================

    session_durations = []


    for session_id, timestamps in session_times.items():

        if len(timestamps) < 2:
            continue

        start_time = min(timestamps)

        end_time = max(timestamps)

        duration = (
            end_time - start_time
        ).total_seconds()


        # Ignore unrealistic sessions
        if 0 <= duration <= 86400:

            session_durations.append(
                duration
            )


    average_session_seconds = (
        sum(session_durations)
        / len(session_durations)
        if session_durations
        else 0
    )


    average_session_minutes = round(
        average_session_seconds / 60,
        1
    )


    # =====================================================
    # HOURLY TRAFFIC
    # =====================================================

    hourly_visitors = defaultdict(set)


    for event in events:

        if (
            event.created_at
            and event.visitor_id
        ):

            hourly_visitors[
                event.created_at.hour
            ].add(
                event.visitor_id
            )


    hourly_labels = [
        f"{hour:02d}:00"
        for hour in range(24)
    ]


    hourly_values = [
        len(
            hourly_visitors.get(
                hour,
                set()
            )
        )
        for hour in range(24)
    ]


    peak_hour_index = (
        max(
            range(24),
            key=lambda hour:
                hourly_values[hour]
        )
        if events
        else 0
    )


    peak_hour = (
        f"{peak_hour_index:02d}:00"
    )


    peak_hour_visitors = (
        hourly_values[
            peak_hour_index
        ]
        if events
        else 0
    )


    # =====================================================
    # DAILY TRAFFIC
    # =====================================================

    daily_visitors = defaultdict(set)


    for event in events:

        if (
            event.created_at
            and event.visitor_id
        ):

            day_key = (
                event.created_at.date()
            )

            daily_visitors[
                day_key
            ].add(
                event.visitor_id
            )


    daily_keys = sorted(
        daily_visitors.keys()
    )[-14:]


    daily_labels = [
        day.strftime("%d %b")
        for day in daily_keys
    ]


    daily_values = [
        len(
            daily_visitors[day]
        )
        for day in daily_keys
    ]


    # =====================================================
    # MONTHLY TRAFFIC
    # =====================================================

    monthly_visitors = defaultdict(set)


    for event in events:

        if (
            event.created_at
            and event.visitor_id
        ):

            month_key = (
                event.created_at.strftime(
                    "%Y-%m"
                )
            )

            monthly_visitors[
                month_key
            ].add(
                event.visitor_id
            )


    monthly_keys = sorted(
        monthly_visitors.keys()
    )[-6:]


    monthly_labels = []


    for month_key in monthly_keys:

        month_date = datetime.strptime(
            month_key,
            "%Y-%m"
        )

        monthly_labels.append(
            month_date.strftime(
                "%b %Y"
            )
        )


    monthly_values = [
        len(
            monthly_visitors[month]
        )
        for month in monthly_keys
    ]


    # =====================================================
    # LOGGED-IN VS GUEST
    # =====================================================

    visitor_type_labels = [
        "Logged-in",
        "Guest"
    ]


    visitor_type_values = [
        logged_in_visitors,
        guest_visitors
    ]


    # =====================================================
    # PRODUCT VIEWS
    # =====================================================

    product_counts = defaultdict(int)

    product_visitors = defaultdict(set)


    for event in events:

        if (
            event.event_type
            == "product_view"
            and event.product_id
        ):

            product_counts[
                event.product_id
            ] += 1

            if event.visitor_id:

                product_visitors[
                    event.product_id
                ].add(
                    event.visitor_id
                )


    top_product_ids = sorted(
        product_counts,
        key=product_counts.get,
        reverse=True
    )[:10]


    top_products = []


    for product_id in top_product_ids:

        product = db.session.get(
            Product,
            product_id
        )

        if not product:
            continue


        image = None


        if product.images:

            image = next(
                (
                    item
                    for item in product.images
                    if item.is_primary
                ),
                product.images[0]
            )


        top_products.append(
            {
                "id": product.id,

                "name": product.name,

                "views": product_counts[
                    product_id
                ],

                "unique_visitors": len(
                    product_visitors.get(
                        product_id,
                        set()
                    )
                ),

                "image_id": (
                    image.id
                    if image
                    else None
                )
            }
        )


    # =====================================================
    # CATEGORY VIEWS
    # =====================================================

    category_counts = defaultdict(int)

    category_visitors = defaultdict(set)


    for event in events:

        if (
            event.event_type
            == "category_view"
            and event.category_id
        ):

            category_counts[
                event.category_id
            ] += 1

            if event.visitor_id:

                category_visitors[
                    event.category_id
                ].add(
                    event.visitor_id
                )


    top_category_ids = sorted(
        category_counts,
        key=category_counts.get,
        reverse=True
    )


    category_traffic = []


    for category_id in top_category_ids:

        category = db.session.get(
            Category,
            category_id
        )

        if not category:
            continue


        category_traffic.append(
            {
                "id": category.id,

                "name": category.name,

                "views": category_counts[
                    category_id
                ],

                "unique_visitors": len(
                    category_visitors.get(
                        category_id,
                        set()
                    )
                ),

                "image_url": (
                    url_for(
                        "admin.category_image",
                        category_id=category.id
                    )
                    if category.image_key
                    else None
                )
            }
        )


    # =====================================================
    # SUBCATEGORY VIEWS
    # =====================================================

    subcategory_counts = defaultdict(int)

    subcategory_visitors = defaultdict(set)


    for event in events:

        if (
            event.event_type
            == "subcategory_view"
            and event.subcategory_id
        ):

            subcategory_counts[
                event.subcategory_id
            ] += 1

            if event.visitor_id:

                subcategory_visitors[
                    event.subcategory_id
                ].add(
                    event.visitor_id
                )


    top_subcategory_ids = sorted(
        subcategory_counts,
        key=subcategory_counts.get,
        reverse=True
    )


    subcategory_traffic = []


    for subcategory_id in top_subcategory_ids:

        subcategory = db.session.get(
            Subcategory,
            subcategory_id
        )

        if not subcategory:
            continue


        subcategory_traffic.append(
            {
                "id": subcategory.id,

                "name": subcategory.name,

                "category_name": (
                    subcategory.category.name
                    if subcategory.category
                    else "—"
                ),

                "views": subcategory_counts[
                    subcategory_id
                ],

                "unique_visitors": len(
                    subcategory_visitors.get(
                        subcategory_id,
                        set()
                    )
                ),

                "image_url": (
                    url_for(
                        "admin.subcategory_image",
                        subcategory_id=subcategory.id
                    )
                    if subcategory.image_key
                    else None
                )
            }
        )


    # =====================================================
    # TOTAL VIEWS
    # =====================================================

    total_page_views = sum(
        1
        for event in events
        if event.event_type == "page_view"
    )


    total_product_views = sum(
        1
        for event in events
        if event.event_type == "product_view"
    )


    total_category_views = sum(
        1
        for event in events
        if event.event_type == "category_view"
    )


    total_subcategory_views = sum(
        1
        for event in events
        if event.event_type == "subcategory_view"
    )


    # =====================================================
    # RENDER TRAFFIC PAGE
    # =====================================================

    return render_template(
        "admin/traffic.html",

        total_visitors=total_visitors,

        logged_in_visitors=logged_in_visitors,

        guest_visitors=guest_visitors,

        total_sessions=total_sessions,

        average_session_minutes=(
            average_session_minutes
        ),

        total_page_views=(
            total_page_views
        ),

        total_product_views=(
            total_product_views
        ),

        total_category_views=(
            total_category_views
        ),

        total_subcategory_views=(
            total_subcategory_views
        ),

        peak_hour=peak_hour,

        peak_hour_visitors=(
            peak_hour_visitors
        ),

        hourly_labels=hourly_labels,

        hourly_values=hourly_values,

        daily_labels=daily_labels,

        daily_values=daily_values,

        monthly_labels=monthly_labels,

        monthly_values=monthly_values,

        visitor_type_labels=(
            visitor_type_labels
        ),

        visitor_type_values=(
            visitor_type_values
        ),

        top_products=top_products,

        category_traffic=(
            category_traffic
        ),

        subcategory_traffic=(
            subcategory_traffic
        )
    )
# =========================================================
# BANNER MANAGEMENT
# =========================================================

@admin_bp.route("/banners")
def banners():

    if "admin_id" not in session:
        return redirect(url_for("admin.login"))

    banners = (
        Banner.query
        .order_by(
            Banner.display_order.asc(),
            Banner.created_at.desc()
        )
        .all()
    )

    return render_template(
        "admin/banners.html",
        banners=banners
    )


# =========================================================
# ADD BANNER
# =========================================================

@admin_bp.route(
    "/banners/add",
    methods=["GET", "POST"]
)
def add_banner():

    if "admin_id" not in session:
        return redirect(url_for("admin.login"))

    if request.method == "POST":

        title = request.form.get(
            "title",
            ""
        ).strip()

        description = request.form.get(
            "description",
            ""
        ).strip()

        button_text = request.form.get(
            "button_text",
            ""
        ).strip()

        button_link = request.form.get(
            "button_link",
            ""
        ).strip()

        display_order_text = request.form.get(
            "display_order",
            "0"
        ).strip()

        is_active = request.form.get(
            "is_active"
        ) == "1"

        image = request.files.get(
            "image"
        )

        # -------------------------------------------------
        # IMAGE VALIDATION
        # -------------------------------------------------

        if not image or not image.filename:

            flash(
                "Banner image is required.",
                "danger"
            )

            return render_template(
                "admin/banner_form.html",
                banner=None
            )

        # -------------------------------------------------
        # DISPLAY ORDER VALIDATION
        # -------------------------------------------------

        try:

            display_order = int(
                display_order_text
            )

        except (
            ValueError,
            TypeError
        ):

            flash(
                "Display order must be a valid whole number.",
                "danger"
            )

            return render_template(
                "admin/banner_form.html",
                banner=None
            )

        if display_order < 0:

            flash(
                "Display order cannot be negative.",
                "danger"
            )

            return render_template(
                "admin/banner_form.html",
                banner=None
            )

        # -------------------------------------------------
        # UPLOAD IMAGE
        # -------------------------------------------------

        image_key = None

        try:

            image_key = upload_image(
                image,
                "banners"
            )

        except ValueError as error:

            flash(
                str(error),
                "danger"
            )

            return render_template(
                "admin/banner_form.html",
                banner=None
            )

        except Exception:

            flash(
                "Unable to upload banner image.",
                "danger"
            )

            return render_template(
                "admin/banner_form.html",
                banner=None
            )

        # -------------------------------------------------
        # ONLY ONE ACTIVE BANNER
        # -------------------------------------------------

        if is_active:

            (
                Banner.query
                .filter(
                    Banner.is_active.is_(True)
                )
                .update(
                    {
                        Banner.is_active: False
                    },
                    synchronize_session=False
                )
            )

        # -------------------------------------------------
        # CREATE BANNER
        # -------------------------------------------------

        banner = Banner(
            title=title or None,
            description=description or None,
            image_key=image_key,
            button_text=button_text or None,
            button_link=button_link or None,
            display_order=display_order,
            is_active=is_active
        )

        try:

            db.session.add(
                banner
            )

            db.session.commit()

        except Exception:

            db.session.rollback()

            if image_key:

                StorageService().delete(
                    image_key
                )

            flash(
                "Unable to create banner.",
                "danger"
            )

            return render_template(
                "admin/banner_form.html",
                banner=None
            )

        flash(
            "Banner created successfully.",
            "success"
        )

        return redirect(
            url_for("admin.banners")
        )

    return render_template(
        "admin/banner_form.html",
        banner=None
    )


# =========================================================
# EDIT BANNER
# =========================================================

@admin_bp.route(
    "/banners/<int:banner_id>/edit",
    methods=["GET", "POST"]
)
def edit_banner(banner_id):

    if "admin_id" not in session:
        return redirect(url_for("admin.login"))

    banner = db.session.get(
        Banner,
        banner_id
    )

    if not banner:

        flash(
            "Banner not found.",
            "danger"
        )

        return redirect(
            url_for("admin.banners")
        )

    if request.method == "POST":

        title = request.form.get(
            "title",
            ""
        ).strip()

        description = request.form.get(
            "description",
            ""
        ).strip()

        button_text = request.form.get(
            "button_text",
            ""
        ).strip()

        button_link = request.form.get(
            "button_link",
            ""
        ).strip()

        display_order_text = request.form.get(
            "display_order",
            "0"
        ).strip()

        is_active = request.form.get(
            "is_active"
        ) == "1"

        image = request.files.get(
            "image"
        )

        # -------------------------------------------------
        # DISPLAY ORDER VALIDATION
        # -------------------------------------------------

        try:

            display_order = int(
                display_order_text
            )

        except (
            ValueError,
            TypeError
        ):

            flash(
                "Display order must be a valid whole number.",
                "danger"
            )

            return render_template(
                "admin/banner_form.html",
                banner=banner
            )

        if display_order < 0:

            flash(
                "Display order cannot be negative.",
                "danger"
            )

            return render_template(
                "admin/banner_form.html",
                banner=banner
            )

        old_image_key = banner.image_key
        new_image_key = None

        # -------------------------------------------------
        # OPTIONAL NEW IMAGE
        # -------------------------------------------------

        if image and image.filename:

            try:

                new_image_key = upload_image(
                    image,
                    "banners"
                )

            except ValueError as error:

                flash(
                    str(error),
                    "danger"
                )

                return render_template(
                    "admin/banner_form.html",
                    banner=banner
                )

            except Exception:

                flash(
                    "Unable to upload banner image.",
                    "danger"
                )

                return render_template(
                    "admin/banner_form.html",
                    banner=banner
                )

        # -------------------------------------------------
        # ONLY ONE ACTIVE BANNER
        # -------------------------------------------------

        if is_active:

            (
                Banner.query
                .filter(
                    Banner.id != banner.id,
                    Banner.is_active.is_(True)
                )
                .update(
                    {
                        Banner.is_active: False
                    },
                    synchronize_session=False
                )
            )

        # -------------------------------------------------
        # UPDATE BANNER
        # -------------------------------------------------

        banner.title = title or None

        banner.description = (
            description or None
        )

        banner.button_text = (
            button_text or None
        )

        banner.button_link = (
            button_link or None
        )

        banner.display_order = (
            display_order
        )

        banner.is_active = (
            is_active
        )

        if new_image_key:

            banner.image_key = (
                new_image_key
            )

        try:

            db.session.commit()

        except Exception:

            db.session.rollback()

            if new_image_key:

                StorageService().delete(
                    new_image_key
                )

            flash(
                "Unable to update banner.",
                "danger"
            )

            return render_template(
                "admin/banner_form.html",
                banner=banner
            )

        # -------------------------------------------------
        # DELETE OLD IMAGE AFTER SUCCESSFUL UPDATE
        # -------------------------------------------------

        if (
            new_image_key
            and old_image_key
        ):

            StorageService().delete(
                old_image_key
            )

        flash(
            "Banner updated successfully.",
            "success"
        )

        return redirect(
            url_for("admin.banners")
        )

    return render_template(
        "admin/banner_form.html",
        banner=banner
    )


# =========================================================
# TOGGLE BANNER STATUS
# =========================================================

@admin_bp.route(
    "/banners/<int:banner_id>/toggle",
    methods=["POST"]
)
def toggle_banner(banner_id):

    if "admin_id" not in session:
        return redirect(url_for("admin.login"))

    banner = db.session.get(
        Banner,
        banner_id
    )

    if not banner:

        flash(
            "Banner not found.",
            "danger"
        )

        return redirect(
            url_for("admin.banners")
        )

    # -----------------------------------------------------
    # ACTIVATE BANNER
    # -----------------------------------------------------

    if not banner.is_active:

        # Deactivate every other banner first.
        (
            Banner.query
            .filter(
                Banner.id != banner.id,
                Banner.is_active.is_(True)
            )
            .update(
                {
                    Banner.is_active: False
                },
                synchronize_session=False
            )
        )

        banner.is_active = True

        message = (
            "Banner activated successfully."
        )

    # -----------------------------------------------------
    # DEACTIVATE CURRENT BANNER
    # -----------------------------------------------------

    else:

        banner.is_active = False

        message = (
            "Banner deactivated successfully."
        )

    try:

        db.session.commit()

    except Exception:

        db.session.rollback()

        flash(
            "Unable to update banner status.",
            "danger"
        )

        return redirect(
            url_for("admin.banners")
        )

    flash(
        message,
        "success"
    )

    return redirect(
        url_for("admin.banners")
    )


# =========================================================
# DELETE BANNER
# =========================================================

@admin_bp.route(
    "/banners/<int:banner_id>/delete",
    methods=["POST"]
)
def delete_banner(banner_id):

    if "admin_id" not in session:
        return redirect(url_for("admin.login"))

    banner = db.session.get(
        Banner,
        banner_id
    )

    if not banner:

        flash(
            "Banner not found.",
            "danger"
        )

        return redirect(
            url_for("admin.banners")
        )

    image_key = banner.image_key

    try:

        db.session.delete(
            banner
        )

        db.session.commit()

    except Exception:

        db.session.rollback()

        flash(
            "Banner could not be deleted.",
            "danger"
        )

        return redirect(
            url_for("admin.banners")
        )

    # -----------------------------------------------------
    # DELETE IMAGE AFTER DATABASE DELETE
    # -----------------------------------------------------

    if image_key:

        try:

            StorageService().delete(
                image_key
            )

        except Exception:

            flash(
                "Banner deleted, but its image file "
                "could not be removed.",
                "warning"
            )

            return redirect(
                url_for("admin.banners")
            )

    flash(
        "Banner permanently deleted.",
        "success"
    )

    return redirect(
        url_for("admin.banners")
    )


# =========================================================
# BANNER IMAGE VIEW
# =========================================================

@admin_bp.route(
    "/banners/<int:banner_id>/image"
)
def banner_image(banner_id):

    if "admin_id" not in session:
        return redirect(url_for("admin.login"))

    banner = db.session.get(
        Banner,
        banner_id
    )

    if not banner or not banner.image_key:

        return "", 404

    storage = StorageService()

    if not storage.exists(banner.image_key):
        return "", 404

    image_file = storage.get_file(
        banner.image_key
    )

    from flask import send_file

    return send_file(
        image_file,
        mimetype="image/webp"
    )
