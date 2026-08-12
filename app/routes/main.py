from flask import (
    Blueprint,
    render_template,
    send_file,
    abort,
    current_app,
    request
)

from pathlib import Path
from app.models import (
    Banner,
    Category,
    Product
)

from app.services.storage_service import StorageService


main_bp = Blueprint(
    "main",
    __name__
)


# =========================================================
# HOME PAGE
# =========================================================

@main_bp.route("/")
def home():

    # -------------------------------------------------
    # ACTIVE HOMEPAGE BANNER
    # -------------------------------------------------

    banner = (
        Banner.query
        .filter_by(
            is_active=True
        )
        .order_by(
            Banner.display_order.asc(),
            Banner.id.asc()
        )
        .first()
    )

    # -------------------------------------------------
    # USE DEFAULT BANNER IF ACTIVE BANNER IS MISSING
    # -------------------------------------------------

    if banner:

        storage = StorageService()

        banner_path = storage.get_path(
            banner.image_key
        )

        if (
            not banner_path
            or not banner_path.exists()
        ):

            banner = None


    # -------------------------------------------------
    # ACTIVE CATEGORIES
    # -------------------------------------------------

    categories = (
        Category.query
        .filter_by(
            is_active=True
        )
        .order_by(
            Category.name.asc()
        )
        .all()
    )


    # -------------------------------------------------
    # FEATURED PRODUCTS
    # -------------------------------------------------

    featured_products = (
        Product.query
        .filter_by(
            is_active=True,
            featured=True
        )
        .order_by(
            Product.created_at.desc()
        )
        .limit(8)
        .all()
    )


    return render_template(
        "home.html",
        banner=banner,
        categories=categories,
        featured_products=featured_products
    )


# =========================================================
# CATEGORY IMAGE
# =========================================================

@main_bp.route(
    "/category-image/<int:category_id>"
)
def category_image(category_id):

    category = Category.query.get_or_404(
        category_id
    )

    if not category.image_key:

        abort(404)


    storage = StorageService()

    image_path = storage.get_path(
        category.image_key
    )


    if not image_path or not image_path.exists():

        abort(404)


    return send_file(
        image_path
    )

# =========================================================
# SUBCATEGORY IMAGE
# =========================================================

@main_bp.route(
    "/subcategory-image/<int:subcategory_id>"
)
def subcategory_image(subcategory_id):

    from app.models import Subcategory

    subcategory = Subcategory.query.get_or_404(
        subcategory_id
    )

    if not subcategory.image_key:

        abort(404)


    storage = StorageService()

    image_path = storage.get_path(
        subcategory.image_key
    )


    if not image_path or not image_path.exists():

        abort(404)


    return send_file(
        image_path
    )
# =========================================================
# PRODUCT IMAGE
# =========================================================

@main_bp.route(
    "/product-image/<int:image_id>"
)
def product_image(image_id):

    # Import here to keep the main model imports clean.
    from app.models import ProductImage


    product_image = ProductImage.query.get_or_404(
        image_id
    )

    if not product_image.image_key:

        abort(404)


    storage = StorageService()

    image_path = storage.get_path(
        product_image.image_key
    )


    if not image_path or not image_path.exists():

        abort(404)


    return send_file(
        image_path
    )


# =========================================================
# BANNER IMAGE
# =========================================================

@main_bp.route(
    "/banner-image/<int:banner_id>"
)
def banner_image(banner_id):

    banner = Banner.query.get_or_404(
        banner_id
    )

    storage = StorageService()

    if banner.image_key:

        image_path = storage.get_path(
            banner.image_key
        )

        if image_path and image_path.exists():

            return send_file(
                image_path
            )

    # -------------------------------------------------
    # FALLBACK TO DEFAULT BANNER
    # -------------------------------------------------

    default_banner = (
        Path(
            current_app.root_path
        )
        .parent
        / "static"
        / "images"
        / "default-banner.svg"
    )

    if default_banner.exists():

        return send_file(
            default_banner
        )

    abort(404)


# =========================================================
# CATEGORIES PAGE
# =========================================================

@main_bp.route(
    "/categories"
)
def categories():

    active_categories = (
        Category.query
        .filter_by(
            is_active=True
        )
        .order_by(
            Category.name.asc()
        )
        .all()
    )

    return render_template(
        "categories.html",
        categories=active_categories
    )

# =========================================================
# PRODUCT LISTING
# =========================================================

@main_bp.route(
    "/products"
)
def products():

    from app.models import (
        Subcategory
    )

    category_slug = (
        request.args.get(
            "category",
            ""
        ).strip()
    )

    subcategory_slug = (
        request.args.get(
            "subcategory",
            ""
        ).strip()
    )


    # -------------------------------------------------
    # CATEGORY FILTER
    # -------------------------------------------------

    selected_category = None

    if category_slug:

        selected_category = (
            Category.query
            .filter_by(
                slug=category_slug,
                is_active=True
            )
            .first()
        )

        if not selected_category:

            return render_template(
                "products.html",
                products=[],
                category=None,
                subcategories=[],
                selected_subcategory=None
            )


    # -------------------------------------------------
    # SUBCATEGORY FILTER
    # -------------------------------------------------

    selected_subcategory = None

    if subcategory_slug:

        selected_subcategory = (
            Subcategory.query
            .filter_by(
                slug=subcategory_slug,
                is_active=True
            )
            .first()
        )

        if not selected_subcategory:

            return render_template(
                "products.html",
                products=[],
                category=selected_category,
                subcategories=[],
                selected_subcategory=None
            )


        # If category is also selected,
        # make sure the subcategory belongs to it.

        if (
            selected_category
            and selected_subcategory.category_id
            != selected_category.id
        ):

            return render_template(
                "products.html",
                products=[],
                category=selected_category,
                subcategories=[],
                selected_subcategory=None
            )


        # If only subcategory was supplied,
        # use its parent category.

        if not selected_category:

            selected_category = (
                Category.query
                .filter_by(
                    id=selected_subcategory.category_id,
                    is_active=True
                )
                .first()
            )


    # -------------------------------------------------
    # SUBCATEGORIES FOR SELECTED CATEGORY
    # -------------------------------------------------

    subcategories = []

    if selected_category:

        subcategories = (
            Subcategory.query
            .filter_by(
                category_id=selected_category.id,
                is_active=True
            )
            .order_by(
                Subcategory.name.asc()
            )
            .all()
        )


    # -------------------------------------------------
    # PRODUCT QUERY
    # -------------------------------------------------

    product_query = (
        Product.query
        .filter_by(
            is_active=True
        )
    )


    if selected_category:

        product_query = product_query.filter(
            Product.category_id
            == selected_category.id
        )


    if selected_subcategory:

        product_query = product_query.filter(
            Product.subcategory_id
            == selected_subcategory.id
        )


    products = (
        product_query
        .order_by(
            Product.created_at.desc()
        )
        .all()
    )


    return render_template(
        "products.html",
        products=products,
        category=selected_category,
        subcategories=subcategories,
        selected_subcategory=selected_subcategory
    )