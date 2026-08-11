from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for
)

from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash

from app import db
from app.models import (
    Admin,
    Brand,
    Category,
    Subcategory
)
from app.services.upload_service import upload_image
from app.services.storage_service import StorageService


admin_bp = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin"
)


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

    image_path = storage.get_path(
        subcategory.image_key
    )

    if not image_path or not image_path.exists():
        return "", 404

    from flask import send_file

    return send_file(
        image_path,
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

    image_path = storage.get_path(
        category.image_key
    )

    if not image_path or not image_path.exists():
        return "", 404

    from flask import send_file

    return send_file(
        image_path,
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

    image_path = storage.get_path(
        brand.logo_key
    )

    if not image_path or not image_path.exists():
        return "", 404

    from flask import send_file

    return send_file(
        image_path,
        mimetype="image/webp"
    )