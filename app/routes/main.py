from flask import (
    Blueprint,
    render_template,
    send_file,
    current_app,
    request,
    redirect,
    url_for,
    flash,
    abort,
    session
)

from pathlib import Path
from app import db, csrf

from app.models import (
    Banner,
    Category,
    Subcategory,
    Brand,
    Product,
    ProductSize,
    CartItem,
    Address,
    Order,
    OrderItem,
    User,
    WishlistItem,
    TrafficEvent
)
from werkzeug.security import (
    check_password_hash,
    generate_password_hash
)

from decimal import Decimal
from datetime import datetime
from difflib import SequenceMatcher
import secrets
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

    # =====================================================
    # READ FILTERS
    # =====================================================

    search_text = (
    request.args.get(
        "search",
        ""
    ).strip()
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

    selected_brands = [
        value.strip()
        for value in request.args.getlist(
            "brand"
        )
        if value.strip()
    ]

    selected_sizes = [
        value.strip()
        for value in request.args.getlist(
            "size"
        )
        if value.strip()
    ]

    min_price_text = (
        request.args.get(
            "min_price",
            ""
        ).strip()
    )

    max_price_text = (
        request.args.get(
            "max_price",
            ""
        ).strip()
    )

    availability = (
        request.args.get(
            "availability",
            ""
        ).strip()
    )

    sort = (
        request.args.get(
            "sort",
            "recommended"
        ).strip()
    )


    # =====================================================
    # SELECTED CATEGORY
    # =====================================================

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
                selected_subcategory=None,
                categories=(
                    Category.query
                    .filter_by(
                        is_active=True
                    )
                    .order_by(
                        Category.name.asc()
                    )
                    .all()
                ),
                brands=[],
                sizes=[],
                min_price=None,
                max_price=None,
                selected_brands=[],
                selected_sizes=[],
                availability="",
                sort="recommended"
            )


    # =====================================================
    # SELECTED SUBCATEGORY
    # =====================================================

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

            selected_subcategory = None

        else:

            # If category is selected, make sure the
            # subcategory belongs to that category.

            if (
                selected_category
                and selected_subcategory.category_id
                != selected_category.id
            ):

                selected_subcategory = None


            # If only subcategory is selected, determine
            # its parent category.

            if (
                selected_subcategory
                and not selected_category
            ):

                selected_category = (
                    Category.query
                    .filter_by(
                        id=selected_subcategory.category_id,
                        is_active=True
                    )
                    .first()
                )


    # =====================================================
    # ALL ACTIVE CATEGORIES
    # =====================================================

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


    # =====================================================
    # SUBCATEGORIES FOR CURRENT CATEGORY
    # =====================================================

    subcategories_query = (
        Subcategory.query
        .filter_by(
            is_active=True
        )
    )

    if selected_category:

        subcategories_query = (
            subcategories_query
            .filter(
                Subcategory.category_id
                == selected_category.id
            )
        )

    subcategories = (
        subcategories_query
        .order_by(
            Subcategory.name.asc()
        )
        .all()
    )


    # =====================================================
    # PRICE VALIDATION
    # =====================================================

    min_price = None
    max_price = None

    if min_price_text:

        try:

            min_price = float(
                min_price_text
            )

        except ValueError:

            min_price = None


    if max_price_text:

        try:

            max_price = float(
                max_price_text
            )

        except ValueError:

            max_price = None


    # =====================================================
    # BASE PRODUCT QUERY
    #
    # This represents the products allowed by:
    # Category + Subcategory
    #
    # It is also used to generate relevant filter
    # options.
    # =====================================================

    base_query = (
        Product.query
        .filter_by(
            is_active=True
        )
    )


    if selected_category:

        base_query = base_query.filter(
            Product.category_id
            == selected_category.id
        )


    if selected_subcategory:

        base_query = base_query.filter(
            Product.subcategory_id
            == selected_subcategory.id
        )


    # =====================================================
    # AVAILABLE BRANDS
    #
    # Only brands belonging to the currently selected
    # category/subcategory are shown.
    # =====================================================

    brand_products_query = base_query


    available_brand_ids = {
        product.brand_id
        for product in (
            brand_products_query
            .with_entities(
                Product.brand_id
            )
            .all()
        )
        if product.brand_id is not None
    }


    brands = (
        Brand.query
        .filter(
            Brand.is_active.is_(True),
            Brand.id.in_(
                available_brand_ids
            )
        )
        .order_by(
            Brand.name.asc()
        )
        .all()
    ) if available_brand_ids else []


    # =====================================================
    # AVAILABLE SIZE / VARIANTS
    #
    # Only variants belonging to products in the current
    # category/subcategory are shown.
    # =====================================================

    size_query = (
        ProductSize.query
        .join(
            Product,
            Product.id
            == ProductSize.product_id
        )
        .filter(
            Product.is_active.is_(True)
        )
    )


    if selected_category:

        size_query = size_query.filter(
            Product.category_id
            == selected_category.id
        )


    if selected_subcategory:

        size_query = size_query.filter(
            Product.subcategory_id
            == selected_subcategory.id
        )


    available_sizes = {
        row[0]
        for row in (
            size_query
            .with_entities(
                ProductSize.size
            )
            .distinct()
            .order_by(
                ProductSize.size.asc()
            )
            .all()
        )
        if row[0]
    }


    sizes = sorted(
        available_sizes,
        key=lambda value: value.lower()
    )


    # =====================================================
    # FINAL PRODUCT QUERY
    # =====================================================

    product_query = base_query
    # =====================================================
    # SEARCH

    search_scores = {}

    if search_text:

        search_words = [
            word.lower()
            for word in search_text.split()
            if word.strip()
        ]


    # -------------------------------------------------
    # GET PRODUCTS AVAILABLE IN CURRENT
    # CATEGORY / SUBCATEGORY
    # -------------------------------------------------

    search_candidates = (
        base_query
        .all()
    )


    matching_product_ids = []


    for product in search_candidates:

        searchable_values = [

            product.name or "",

            (
                product.brand.name
                if product.brand
                else ""
            ),

            (
                product.category.name
                if product.category
                else ""
            ),

            (
                product.subcategory.name
                if product.subcategory
                else ""
            )
        ]


        searchable_text = " ".join(
            searchable_values
        ).lower()


        # -------------------------------------------------
        # DIRECT MATCH
        # -------------------------------------------------

        if search_text.lower() in searchable_text:

            matching_product_ids.append(
                product.id
            )

            search_scores[product.id] = 100

            continue


        # -------------------------------------------------
        # WORD / FUZZY MATCH
        # -------------------------------------------------

        best_score = 0


        for search_word in search_words:

            word_best_score = 0


            for value in searchable_values:

                value = value.lower().strip()

                if not value:
                    continue


                # Exact word / partial word match

                if search_word in value:

                    word_best_score = 95

                    break


                # Compare against individual words

                value_words = value.split()


                for value_word in value_words:

                    similarity = (
                        SequenceMatcher(
                            None,
                            search_word,
                            value_word
                        ).ratio()
                        * 100
                    )


                    if similarity > word_best_score:

                        word_best_score = similarity


            best_score = max(
                best_score,
                word_best_score
            )


        # -------------------------------------------------
        # ACCEPT REASONABLE FUZZY MATCH
        # -------------------------------------------------

        if best_score >= 75:

            matching_product_ids.append(
                product.id
            )

            search_scores[product.id] = (
                best_score
            )


    # -------------------------------------------------
    # NO SEARCH RESULTS
    # -------------------------------------------------

    if matching_product_ids:

        product_query = product_query.filter(
            Product.id.in_(
                matching_product_ids
            )
        )

    else:

        product_query = product_query.filter(
            Product.id == -1
        )


    # -----------------------------------------------------
    # BRAND FILTER
    # -----------------------------------------------------

    if selected_brands:

        product_query = product_query.filter(
            Product.brand_id.in_(
                Brand.id
                for Brand in brands
                if Brand.slug in selected_brands
            )
        )


    # -----------------------------------------------------
    # PRICE FILTER
    # -----------------------------------------------------

    if min_price is not None:

        product_query = product_query.filter(
            Product.price >= min_price
        )


    if max_price is not None:

        product_query = product_query.filter(
            Product.price <= max_price
        )


    # -----------------------------------------------------
    # SIZE / VARIANT FILTER
    # -----------------------------------------------------

    if selected_sizes:

        product_query = product_query.filter(
            Product.sizes.any(
                ProductSize.size.in_(
                    selected_sizes
                )
            )
        )


    # -----------------------------------------------------
    # AVAILABILITY
    # -----------------------------------------------------

    if availability == "in_stock":

        product_query = product_query.filter(
            Product.stock_quantity > 0
        )


    # =====================================================
    # SORTING
    # =====================================================

    if sort == "price_low":

        product_query = product_query.order_by(
            Product.price.asc()
        )

    elif sort == "price_high":

        product_query = product_query.order_by(
            Product.price.desc()
        )

    elif sort == "name_az":

        product_query = product_query.order_by(
            Product.name.asc()
        )

    elif sort == "name_za":

        product_query = product_query.order_by(
            Product.name.desc()
        )

    else:

        product_query = product_query.order_by(
            Product.created_at.desc()
        )


    # =====================================================
    # FINAL PRODUCTS
    # =====================================================

    products = (
        product_query
        .all()
    )

    # =====================================================
    # SEARCH RELEVANCE
    #
    # When the customer is searching and has not selected
    # another sorting method, show the closest matches first.
    # =====================================================

    if search_text and sort == "recommended":

        products.sort(
            key=lambda product: search_scores.get(
                product.id,
                0
            ),
            reverse=True
        )


    # =====================================================
    # PRICE RANGE FOR CURRENT CATEGORY/SUBCATEGORY
    # =====================================================

    current_prices = [
        float(product.price)
        for product in (
            base_query
            .with_entities(
                Product.price
            )
            .all()
        )
        if product.price is not None
    ]


    price_min = (
        min(current_prices)
        if current_prices
        else 0
    )

    price_max = (
        max(current_prices)
        if current_prices
        else 0
    )


    return render_template(
        "products.html",
        products=products,
        category=selected_category,
        search_text=search_text,
        subcategories=subcategories,
        selected_subcategory=selected_subcategory,
        categories=categories,
        brands=brands,
        sizes=sizes,
        selected_brands=selected_brands,
        selected_sizes=selected_sizes,
        min_price=min_price,
        max_price=max_price,
        price_min=price_min,
        price_max=price_max,
        availability=availability,
        sort=sort
    )


# =========================================================
# PRODUCT DETAILS
# =========================================================

@main_bp.route(
    "/products/<string:slug>"
)
def product_detail(slug):

    # -----------------------------------------------------
    # ACTIVE PRODUCT
    # -----------------------------------------------------

    product = (
        Product.query
        .filter_by(
            slug=slug,
            is_active=True
        )
        .first()
    )

    if not product:

        abort(404)


    # -----------------------------------------------------
    # RELATED PRODUCTS
    # -----------------------------------------------------

    related_products = (
        Product.query
        .filter(
            Product.is_active.is_(True),
            Product.category_id == product.category_id,
            Product.id != product.id
        )
        .order_by(
            Product.created_at.desc()
        )
        .limit(4)
        .all()
    )


    return render_template(
        "product_detail.html",
        product=product,
        related_products=related_products
    )


# =========================================================
# ADD TO CART
# =========================================================

@main_bp.route(
    "/cart/add",
    methods=["POST"]
)
def add_to_cart():

    # -----------------------------------------------------
    # LOGIN REQUIRED
    # -----------------------------------------------------

    user_id = session.get("user_id")

    if not user_id:

        flash(
            "Please login to add products to your cart.",
            "warning"
        )

        return redirect(
            url_for(
                "auth.login"
            )
        )


    # -----------------------------------------------------
    # PRODUCT
    # -----------------------------------------------------

    product_id = request.form.get(
        "product_id",
        type=int
    )

    if not product_id:

        flash(
            "Invalid product.",
            "danger"
        )

        return redirect(
            url_for(
                "main.home"
            )
        )


    product = (
        Product.query
        .filter_by(
            id=product_id,
            is_active=True
        )
        .first()
    )

    if not product:

        flash(
            "Product is no longer available.",
            "danger"
        )

        return redirect(
            url_for(
                "main.home"
            )
        )


    # -----------------------------------------------------
    # VARIANT
    # -----------------------------------------------------

    product_size_id = request.form.get(
        "product_size_id",
        type=int
    )


    variant = None


    if product.sizes:

        if not product_size_id:

            flash(
                "Please select a size or variant.",
                "warning"
            )

            return redirect(
                url_for(
                    "main.product_detail",
                    slug=product.slug
                )
            )


        variant = (
            ProductSize.query
            .filter_by(
                id=product_size_id,
                product_id=product.id
            )
            .first()
        )


        if not variant:

            flash(
                "Selected variant is invalid.",
                "danger"
            )

            return redirect(
                url_for(
                    "main.product_detail",
                    slug=product.slug
                )
            )


    # -----------------------------------------------------
    # QUANTITY
    # -----------------------------------------------------

    quantity = request.form.get(
        "quantity",
        type=int
    )


    if not quantity or quantity < 1:

        flash(
            "Quantity must be at least 1.",
            "warning"
        )

        return redirect(
            url_for(
                "main.product_detail",
                slug=product.slug
            )
        )


    # -----------------------------------------------------
    # AVAILABLE STOCK
    # -----------------------------------------------------

    available_stock = (
        variant.quantity
        if variant
        else product.stock_quantity
    )


    if available_stock <= 0:

        flash(
            "This product is currently out of stock.",
            "danger"
        )

        return redirect(
            url_for(
                "main.product_detail",
                slug=product.slug
            )
        )


    if quantity > available_stock:

        flash(
            f"Only {available_stock} item(s) are available.",
            "warning"
        )

        return redirect(
            url_for(
                "main.product_detail",
                slug=product.slug
            )
        )


    # -----------------------------------------------------
    # FIND EXISTING CART ITEM
    # -----------------------------------------------------

    cart_item_query = (
        CartItem.query
        .filter_by(
            user_id=user_id,
            product_id=product.id
        )
    )


    if variant:

        cart_item = (
            cart_item_query
            .filter_by(
                product_size_id=variant.id
            )
            .first()
        )

    else:

        cart_item = (
            cart_item_query
            .filter(
                CartItem.product_size_id.is_(None)
            )
            .first()
        )


    # -----------------------------------------------------
    # ADD / UPDATE CART ITEM
    # -----------------------------------------------------

    if cart_item:

        new_quantity = (
            cart_item.quantity
            + quantity
        )


        if new_quantity > available_stock:

            flash(
                f"You can only have {available_stock} item(s) "
                "of this variant in your cart.",
                "warning"
            )

            return redirect(
                url_for(
                    "main.product_detail",
                    slug=product.slug
                )
            )


        cart_item.quantity = new_quantity


    else:

        cart_item = CartItem(
            user_id=user_id,
            product_id=product.id,
            product_size_id=(
                variant.id
                if variant
                else None
            ),
            quantity=quantity
        )

        db.session.add(
            cart_item
        )


    db.session.commit()


    flash(
        "Product added to cart.",
        "success"
    )


    return redirect(
        url_for(
            "main.product_detail",
            slug=product.slug
        )
    )

# =========================================================
# CART PAGE
# =========================================================

@main_bp.route("/cart")
def cart():

    # -----------------------------------------------------
    # LOGIN REQUIRED
    # -----------------------------------------------------

    user_id = session.get("user_id")

    if not user_id:
        return redirect(
            url_for("auth.login")
        )

    # -----------------------------------------------------
    # GET CART ITEMS
    # -----------------------------------------------------

    cart_items = (
        CartItem.query
        .filter_by(
            user_id=user_id
        )
        .order_by(
            CartItem.created_at.desc()
        )
        .all()
    )

    # -----------------------------------------------------
    # CALCULATE TOTAL + CHECK CURRENT STOCK
    # -----------------------------------------------------

    cart_total = 0

    for item in cart_items:

        # -------------------------------------------------
        # CURRENT PRICE
        #
        # Variant products use the current variant price.
        # Normal products use the current product price.
        # -------------------------------------------------

        if item.product_size:

            item_price = (
                item.product_size.price
            )

        else:

            item_price = (
                item.product.price
            )


        # -------------------------------------------------
        # CURRENT AVAILABLE STOCK
        #
        # Variant products use the current variant quantity.
        # Normal products use the current product stock.
        # -------------------------------------------------

        if item.product_size:

            available_stock = (
                item.product_size.quantity
            )

        else:

            available_stock = (
                item.product.stock_quantity
            )


        # -------------------------------------------------
        # STOCK STATUS
        #
        # Do not automatically change the cart quantity.
        # We only mark the item so the template can display
        # a warning.
        # -------------------------------------------------

        item.stock_issue = False

        if available_stock <= 0:

            item.stock_issue = True

        elif item.quantity > available_stock:

            item.stock_issue = True


        # -------------------------------------------------
        # ITEM SUBTOTAL
        # -------------------------------------------------

        item.subtotal = (
            item_price * item.quantity
        )

        cart_total += item.subtotal

    # -----------------------------------------------------
    # RENDER CART
    # -----------------------------------------------------

    return render_template(
        "cart.html",
        cart_items=cart_items,
        cart_total=cart_total
    )


    # =========================================================
# UPDATE CART QUANTITY
# =========================================================

@main_bp.route(
    "/cart/update/<int:cart_item_id>",
    methods=["POST"]
)
def update_cart_quantity(cart_item_id):

    # -----------------------------------------------------
    # LOGIN REQUIRED
    # -----------------------------------------------------

    user_id = session.get("user_id")

    if not user_id:

        flash(
            "Please login to update your cart.",
            "warning"
        )

        return redirect(
            url_for("auth.login")
        )


    # -----------------------------------------------------
    # CART ITEM
    #
    # Only allow the logged-in user to update their own
    # cart item.
    # -----------------------------------------------------

    cart_item = (
        CartItem.query
        .filter_by(
            id=cart_item_id,
            user_id=user_id
        )
        .first()
    )

    if not cart_item:

        flash(
            "Cart item not found.",
            "danger"
        )

        return redirect(
            url_for("main.cart")
        )


    # -----------------------------------------------------
    # NEW QUANTITY
    # -----------------------------------------------------

    quantity = request.form.get(
        "quantity",
        type=int
    )


    if not quantity or quantity < 1:

        flash(
            "Quantity must be at least 1.",
            "warning"
        )

        return redirect(
            url_for("main.cart")
        )


    # -----------------------------------------------------
    # AVAILABLE STOCK
    #
    # Variant products use variant quantity.
    # Normal products use product stock_quantity.
    # -----------------------------------------------------

    if cart_item.product_size:

        available_stock = (
            cart_item.product_size.quantity
        )

    else:

        available_stock = (
            cart_item.product.stock_quantity
        )


    # -----------------------------------------------------
    # OUT OF STOCK
    # -----------------------------------------------------

    if available_stock <= 0:

        flash(
            "This item is currently out of stock.",
            "danger"
        )

        return redirect(
            url_for("main.cart")
        )


    # -----------------------------------------------------
    # STOCK LIMIT
    # -----------------------------------------------------

    if quantity > available_stock:

        flash(
            f"Only {available_stock} item(s) are available.",
            "warning"
        )

        return redirect(
            url_for("main.cart")
        )


    # -----------------------------------------------------
    # UPDATE QUANTITY
    # -----------------------------------------------------

    cart_item.quantity = quantity

    db.session.commit()


    flash(
        "Cart quantity updated.",
        "success"
    )


    return redirect(
        url_for("main.cart")
    )

# =========================================================
# REMOVE CART ITEM
# =========================================================

@main_bp.route(
    "/cart/remove/<int:cart_item_id>",
    methods=["POST"]
)
def remove_cart_item(cart_item_id):

    # -----------------------------------------------------
    # LOGIN REQUIRED
    # -----------------------------------------------------

    user_id = session.get("user_id")

    if not user_id:

        flash(
            "Please login to manage your cart.",
            "warning"
        )

        return redirect(
            url_for("auth.login")
        )


    # -----------------------------------------------------
    # CART ITEM
    #
    # Only allow the logged-in user to remove their own
    # cart item.
    # -----------------------------------------------------

    cart_item = (
        CartItem.query
        .filter_by(
            id=cart_item_id,
            user_id=user_id
        )
        .first()
    )

    if not cart_item:

        flash(
            "Cart item not found.",
            "danger"
        )

        return redirect(
            url_for("main.cart")
        )


    # -----------------------------------------------------
    # REMOVE CART ITEM
    # -----------------------------------------------------

    db.session.delete(
        cart_item
    )

    db.session.commit()


    flash(
        "Item removed from cart.",
        "success"
    )


    return redirect(
        url_for("main.cart")
    )


# =========================================================
# WISHLIST
# =========================================================

@main_bp.route("/wishlist")
def wishlist():

    # -----------------------------------------------------
    # LOGIN REQUIRED
    # -----------------------------------------------------

    user_id = session.get("user_id")

    if not user_id:

        flash(
            "Please login to view your wishlist.",
            "warning"
        )

        return redirect(
            url_for("auth.login")
        )


    # -----------------------------------------------------
    # GET WISHLIST ITEMS
    # -----------------------------------------------------

    wishlist_items = (
        WishlistItem.query
        .filter_by(
            user_id=user_id
        )
        .join(Product)
        .filter(
            Product.is_active.is_(True)
        )
        .order_by(
            WishlistItem.created_at.desc()
        )
        .all()
    )


    return render_template(
        "wishlist.html",
        wishlist_items=wishlist_items
    )


# =========================================================
# ADD TO WISHLIST
# =========================================================

@main_bp.route(
    "/wishlist/add",
    methods=["POST"]
)
def add_to_wishlist():

    # -----------------------------------------------------
    # LOGIN REQUIRED
    # -----------------------------------------------------

    user_id = session.get("user_id")

    if not user_id:

        flash(
            "Please login to add products to your wishlist.",
            "warning"
        )

        return redirect(
            url_for("auth.login")
        )


    product_id = request.form.get(
        "product_id",
        type=int
    )


    if not product_id:

        flash(
            "Invalid product.",
            "danger"
        )

        return redirect(
            url_for("main.products")
        )


    # -----------------------------------------------------
    # PRODUCT
    # -----------------------------------------------------

    product = (
        Product.query
        .filter_by(
            id=product_id,
            is_active=True
        )
        .first()
    )


    if not product:

        flash(
            "Product is no longer available.",
            "danger"
        )

        return redirect(
            url_for("main.products")
        )


    # -----------------------------------------------------
    # CHECK EXISTING WISHLIST ITEM
    # -----------------------------------------------------

    existing_item = (
        WishlistItem.query
        .filter_by(
            user_id=user_id,
            product_id=product.id
        )
        .first()
    )


    if existing_item:

        flash(
            "Product is already in your wishlist.",
            "info"
        )

        return redirect(
            url_for(
                "main.product_detail",
                slug=product.slug
            )
        )


    # -----------------------------------------------------
    # ADD PRODUCT
    # -----------------------------------------------------

    wishlist_item = WishlistItem(
        user_id=user_id,
        product_id=product.id
    )


    db.session.add(
        wishlist_item
    )

    db.session.commit()


    flash(
        "Product added to wishlist.",
        "success"
    )


    return redirect(
        url_for(
            "main.product_detail",
            slug=product.slug
        )
    )


# =========================================================
# REMOVE FROM WISHLIST
# =========================================================

@main_bp.route(
    "/wishlist/remove/<int:wishlist_id>",
    methods=["POST"]
)
def remove_from_wishlist(wishlist_id):

    # -----------------------------------------------------
    # LOGIN REQUIRED
    # -----------------------------------------------------

    user_id = session.get("user_id")

    if not user_id:

        flash(
            "Please login to manage your wishlist.",
            "warning"
        )

        return redirect(
            url_for("auth.login")
        )


    # -----------------------------------------------------
    # FIND CUSTOMER'S OWN WISHLIST ITEM
    # -----------------------------------------------------

    wishlist_item = (
        WishlistItem.query
        .filter_by(
            id=wishlist_id,
            user_id=user_id
        )
        .first()
    )


    if not wishlist_item:

        flash(
            "Wishlist item not found.",
            "danger"
        )

        return redirect(
            url_for("main.wishlist")
        )


    # -----------------------------------------------------
    # REMOVE
    # -----------------------------------------------------

    db.session.delete(
        wishlist_item
    )

    db.session.commit()


    flash(
        "Product removed from wishlist.",
        "success"
    )


    return redirect(
        url_for("main.wishlist")
    )

# =========================================================
# CHECKOUT
# =========================================================

@main_bp.route(
    "/checkout",
    methods=["GET"]
)
def checkout():

    # -----------------------------------------------------
    # LOGIN REQUIRED
    # -----------------------------------------------------

    user_id = session.get("user_id")

    if not user_id:

        flash(
            "Please login to continue to checkout.",
            "warning"
        )

        return redirect(
            url_for("auth.login")
        )


    # -----------------------------------------------------
    # GET CART ITEMS
    # -----------------------------------------------------

    cart_items = (
        CartItem.query
        .filter_by(
            user_id=user_id
        )
        .order_by(
            CartItem.created_at.desc()
        )
        .all()
    )


    if not cart_items:

        flash(
            "Your cart is empty.",
            "warning"
        )

        return redirect(
            url_for("main.cart")
        )


    # -----------------------------------------------------
    # CALCULATE CURRENT TOTAL
    # -----------------------------------------------------

    subtotal = Decimal("0.00")

    for item in cart_items:

        if item.product_size:

            item_price = Decimal(
                str(item.product_size.price)
            )

            available_stock = (
                item.product_size.quantity
            )

        else:

            item_price = Decimal(
                str(item.product.price)
            )

            available_stock = (
                item.product.stock_quantity
            )


        # -------------------------------------------------
        # STOCK VALIDATION
        # -------------------------------------------------

        if available_stock <= 0:

            flash(
                f"{item.product.name} is out of stock.",
                "danger"
            )

            return redirect(
                url_for("main.cart")
            )


        if item.quantity > available_stock:

            flash(
                f"Only {available_stock} item(s) of "
                f"{item.product.name} are available.",
                "warning"
            )

            return redirect(
                url_for("main.cart")
            )


        item.subtotal = (
            item_price * item.quantity
        )

        subtotal += item.subtotal


    # -----------------------------------------------------
    # DELIVERY FEE
    #
    # Below ₹1,000  → ₹100
    # ₹1,000+       → FREE
    # -----------------------------------------------------

    if subtotal < Decimal("1000.00"):

        delivery_fee = Decimal("100.00")

    else:

        delivery_fee = Decimal("0.00")


    total_amount = (
        subtotal
        + delivery_fee
    )


    # -----------------------------------------------------
    # CURRENT USER
    # -----------------------------------------------------

    user = (
        User.query
        .filter_by(
            id=user_id
        )
        .first()
    )


    if not user:

        flash(
            "Unable to load your account information.",
            "danger"
        )

        return redirect(
            url_for("auth.login")
        )


    # -----------------------------------------------------
    # SAVED ADDRESSES
    # -----------------------------------------------------

    addresses = (
        Address.query
        .filter_by(
            user_id=user_id
        )
        .order_by(
            Address.is_default.desc(),
            Address.created_at.desc()
        )
        .all()
    )


    # -----------------------------------------------------
    # RENDER CHECKOUT
    # -----------------------------------------------------

    return render_template(
        "checkout.html",

        cart_items=cart_items,

        subtotal=subtotal,

        delivery_fee=delivery_fee,

        total_amount=total_amount,

        addresses=addresses,

        account_name=user.full_name,

        account_phone=user.phone,

        account_email=user.email
    )


# =========================================================
# PLACE ORDER
# =========================================================

@main_bp.route(
    "/checkout/place-order",
    methods=["POST"]
)
def place_order():

    # -----------------------------------------------------
    # LOGIN REQUIRED
    # -----------------------------------------------------

    user_id = session.get("user_id")

    if not user_id:

        flash(
            "Please login to place an order.",
            "warning"
        )

        return redirect(
            url_for("auth.login")
        )


    # -----------------------------------------------------
    # CART
    # -----------------------------------------------------

    cart_items = (
        CartItem.query
        .filter_by(
            user_id=user_id
        )
        .order_by(
            CartItem.created_at.asc()
        )
        .all()
    )


    if not cart_items:

        flash(
            "Your cart is empty.",
            "warning"
        )

        return redirect(
            url_for("main.cart")
        )


    # -----------------------------------------------------
    # CUSTOMER / RECIPIENT DETAILS
    # -----------------------------------------------------

    full_name = (
        request.form.get(
            "full_name",
            ""
        )
        .strip()
    )

    phone = (
        request.form.get(
            "phone",
            ""
        )
        .strip()
    )

    email = (
        request.form.get(
            "email",
            ""
        )
        .strip()
    )

    address_line = (
        request.form.get(
            "address_line",
            ""
        )
        .strip()
    )

    city = (
        request.form.get(
            "city",
            ""
        )
        .strip()
    )

    state = (
        request.form.get(
            "state",
            ""
        )
        .strip()
    )

    pincode = (
        request.form.get(
            "pincode",
            ""
        )
        .strip()
    )

    save_address = (
    request.form.get(
        "save_address"
    )
    == "1"
    )


    # -----------------------------------------------------
    # BASIC VALIDATION
    # -----------------------------------------------------

    if not full_name:

        flash(
            "Please enter the recipient name.",
            "warning"
        )

        return redirect(
            url_for("main.checkout")
        )


    if not phone:

        flash(
            "Please enter a mobile number.",
            "warning"
        )

        return redirect(
            url_for("main.checkout")
        )


    if not email:

        flash(
            "Please enter an email address.",
            "warning"
        )

        return redirect(
            url_for("main.checkout")
        )


    if not address_line:

        flash(
            "Please enter the delivery address.",
            "warning"
        )

        return redirect(
            url_for("main.checkout")
        )


    if not city or not state or not pincode:

        flash(
            "Please complete the delivery address.",
            "warning"
        )

        return redirect(
            url_for("main.checkout")
        )


    # -----------------------------------------------------
    # CART REVALIDATION
    #
    # Never trust prices or stock values coming from
    # the browser.
    # -----------------------------------------------------

    subtotal = Decimal("0.00")

    validated_items = []


    for item in cart_items:

        product = item.product
        variant = item.product_size


        if not product or not product.is_active:

            flash(
                "One of the products in your cart is no longer available.",
                "danger"
            )

            return redirect(
                url_for("main.cart")
            )


        # -------------------------------------------------
        # VARIANT PRODUCT
        # -------------------------------------------------

        if variant:

            current_price = Decimal(
                str(variant.price)
            )

            available_stock = (
                variant.quantity
            )

            variant_name = variant.size


        # -------------------------------------------------
        # NORMAL PRODUCT
        # -------------------------------------------------

        else:

            current_price = Decimal(
                str(product.price)
            )

            available_stock = (
                product.stock_quantity
            )

            variant_name = None


        # -------------------------------------------------
        # STOCK CHECK
        # -------------------------------------------------

        if available_stock <= 0:

            flash(
                f"{product.name} is out of stock.",
                "danger"
            )

            return redirect(
                url_for("main.cart")
            )


        if item.quantity > available_stock:

            flash(
                f"Only {available_stock} item(s) of "
                f"{product.name} are available.",
                "warning"
            )

            return redirect(
                url_for("main.cart")
            )


        item_total = (
            current_price
            * item.quantity
        )


        subtotal += item_total


        validated_items.append(
            {
                "cart_item": item,
                "product": product,
                "variant": variant,
                "variant_name": variant_name,
                "price": current_price,
                "quantity": item.quantity,
                "total": item_total
            }
        )


    # -----------------------------------------------------
    # DELIVERY FEE
    # -----------------------------------------------------

    if subtotal < Decimal("1000.00"):

        delivery_fee = Decimal("100.00")

    else:

        delivery_fee = Decimal("0.00")


    total_amount = (
        subtotal
        + delivery_fee
    )


    # -----------------------------------------------------
    # GENERATE ORDER NUMBER
    # -----------------------------------------------------

    order_number = (
        "SE"
        + datetime.now().strftime("%Y%m%d")
        + "-"
        + secrets.token_hex(3).upper()
    )


    # -----------------------------------------------------
    # CREATE ORDER
    # -----------------------------------------------------

    try:

    # -------------------------------------------------
    # SAVE NEW ADDRESS
    # -------------------------------------------------

        if save_address:

            existing_addresses = (
                Address.query
                .filter_by(
                    user_id=user_id
                )
                .all()
            )

            new_address = Address(
                user_id=user_id,
                full_name=full_name,
                phone=phone,
                address_line=address_line,
                city=city,
                state=state,
                pincode=pincode,
                is_default=(
                    len(existing_addresses) == 0
                )
            )

            db.session.add(
                new_address
            )


    # -------------------------------------------------
    # CREATE ORDER
    # -------------------------------------------------

        order = Order(
                user_id=user_id,
                order_number=order_number,

                subtotal=subtotal,
                delivery_fee=delivery_fee,
                total_amount=total_amount,

                # Payment is not implemented yet.
                # Existing database requires COD.
                payment_method="COD",

                status="PENDING",

                shipping_full_name=full_name,
                shipping_phone=phone,
                shipping_email=email,
                shipping_address_line=address_line,
                shipping_city=city,
                shipping_state=state,
                shipping_pincode=pincode
            )

        db.session.add(order)

        db.session.flush()


        # -------------------------------------------------
        # CREATE ORDER ITEMS + REDUCE STOCK
        # -------------------------------------------------

        for data in validated_items:

            cart_item = data["cart_item"]
            product = data["product"]
            variant = data["variant"]


            order_item = OrderItem(

                order_id=order.id,

                product_id=product.id,

                product_size_id=(
                    variant.id
                    if variant
                    else None
                ),

                product_name=product.name,

                sku=product.sku,

                variant_name=data["variant_name"],

                quantity=data["quantity"],

                unit_price=data["price"],

                total_price=data["total"]
            )


            db.session.add(
                order_item
            )


            # -------------------------------------------------
            # REDUCE INVENTORY
            # -------------------------------------------------

            if variant:

                variant.quantity -= (
                    data["quantity"]
                )

            else:

                product.stock_quantity -= (
                    data["quantity"]
                )


            # -------------------------------------------------
            # REMOVE CART ITEM
            # -------------------------------------------------

            db.session.delete(
                cart_item
            )


        db.session.commit()


    except Exception as error:

        db.session.rollback()

        current_app.logger.exception(
            "ORDER CREATION FAILED: %s",
            error
        )

        flash(
            "Unable to place your order right now. "
            "Please try again.",
            "danger"
        )

        return redirect(
            url_for("main.checkout")
        )


    # -----------------------------------------------------
    # ORDER SUCCESS
    # -----------------------------------------------------

    return redirect(
        url_for(
            "main.order_confirmation",
            order_number=order.order_number
        )
    )

# =========================================================
# ORDER CONFIRMATION / ORDER DETAILS
# =========================================================

@main_bp.route(
    "/orders/<string:order_number>"
)
def order_confirmation(order_number):

    # -----------------------------------------------------
    # LOGIN REQUIRED
    # -----------------------------------------------------

    user_id = session.get("user_id")

    if not user_id:

        flash(
            "Please login to view your order.",
            "warning"
        )

        return redirect(
            url_for("auth.login")
        )


    # -----------------------------------------------------
    # GET ORDER
    #
    # Only allow the logged-in customer to view their
    # own order.
    # -----------------------------------------------------

    order = (
        Order.query
        .filter_by(
            order_number=order_number,
            user_id=user_id
        )
        .first()
    )


    if not order:

        flash(
            "Order not found.",
            "danger"
        )

        return redirect(
            url_for("main.cart")
        )


    # -----------------------------------------------------
    # SIMULATED ORDER STATUS
    #
    # 0:00  - PENDING
    # 0:30  - CONFIRMED
    # 2:30  - OUT FOR DELIVERY
    # 4:30  - DELIVERED
    # -----------------------------------------------------

    if order.created_at:

        elapsed_seconds = (
            datetime.utcnow()
            - order.created_at
        ).total_seconds()

    else:

        elapsed_seconds = 0


    if elapsed_seconds >= 270:

        simulated_status = "DELIVERED"

    elif elapsed_seconds >= 150:

        simulated_status = "SHIPPED"

    elif elapsed_seconds >= 30:

        simulated_status = "CONFIRMED"

    else:

        simulated_status = "PENDING"


    # -----------------------------------------------------
    # UPDATE DATABASE STATUS
    #
    # This keeps the database synchronized with the
    # simulated delivery progression.
    # -----------------------------------------------------

    if order.status != simulated_status:

        order.status = simulated_status

        db.session.commit()


    # -----------------------------------------------------
    # DISPLAY STATUS
    #
    # Database uses SHIPPED, but the customer sees:
    # OUT FOR DELIVERY
    # -----------------------------------------------------

    if simulated_status == "SHIPPED":

        display_status = "OUT FOR DELIVERY"

    else:

        display_status = simulated_status


    # -----------------------------------------------------
    # ORDER ITEMS
    # -----------------------------------------------------

    order_items = (
        OrderItem.query
        .filter_by(
            order_id=order.id
        )
        .all()
    )


    # -----------------------------------------------------
    # RENDER ORDER DETAILS
    # -----------------------------------------------------

    return render_template(
        "order_confirmation.html",

        order=order,

        order_items=order_items,

        display_status=display_status
    )

# =========================================================
# CUSTOMER PROFILE
# =========================================================

@main_bp.route("/profile")
def profile():

    # -----------------------------------------------------
    # LOGIN REQUIRED
    # -----------------------------------------------------

    user_id = session.get("user_id")

    if not user_id:

        flash(
            "Please login to access your profile.",
            "warning"
        )

        return redirect(
            url_for("auth.login")
        )


    # -----------------------------------------------------
    # USER
    # -----------------------------------------------------

    user = (
        User.query
        .filter_by(id=user_id)
        .first()
    )

    if not user:

        session.clear()

        flash(
            "Your account could not be found.",
            "danger"
        )

        return redirect(
            url_for("auth.login")
        )


    # -----------------------------------------------------
    # SAVED ADDRESSES
    # -----------------------------------------------------

    addresses = (
        Address.query
        .filter_by(user_id=user_id)
        .order_by(
            Address.is_default.desc(),
            Address.created_at.desc()
        )
        .all()
    )


    # -----------------------------------------------------
    # ORDERS
    # -----------------------------------------------------

    orders = (
        Order.query
        .filter_by(user_id=user_id)
        .order_by(
            Order.created_at.desc()
        )
        .all()
    )

    order_items_map = {}

    for order in orders:

        order_items_map[order.id] = (
            OrderItem.query
            .filter_by(
                order_id=order.id
            )
            .all()
        )


    # -----------------------------------------------------
    # SIMULATED ORDER STATUS
    # -----------------------------------------------------

    for order in orders:

        if order.created_at:

            elapsed_seconds = (
                datetime.utcnow()
                - order.created_at
            ).total_seconds()

        else:

            elapsed_seconds = 0


        if elapsed_seconds >= 270:

            simulated_status = "DELIVERED"

        elif elapsed_seconds >= 150:

            simulated_status = "SHIPPED"

        elif elapsed_seconds >= 30:

            simulated_status = "CONFIRMED"

        else:

            simulated_status = "PENDING"


        if order.status != simulated_status:

            order.status = simulated_status


        if simulated_status == "SHIPPED":

            order.display_status = "OUT FOR DELIVERY"

        else:

            order.display_status = simulated_status


    db.session.commit()


    # -----------------------------------------------------
    # CURRENT PROFILE SECTION
    # -----------------------------------------------------

    section = request.args.get(
        "section",
        "profile"
    )

    if section not in (
        "profile",
        "orders",
        "addresses"
    ):

        section = "profile"


    return render_template(
        "profile.html",
        user=user,
        addresses=addresses,
        orders=orders,
        order_items_map=order_items_map,
        section=section
    )


# =========================================================
# CHANGE PASSWORD
# =========================================================

@main_bp.route(
    "/profile/change-password",
    methods=["POST"]
)
def change_password():

    user_id = session.get("user_id")

    if not user_id:

        flash(
            "Please login to continue.",
            "warning"
        )

        return redirect(
            url_for("auth.login")
        )


    user = (
        User.query
        .filter_by(id=user_id)
        .first()
    )


    if not user:

        session.clear()

        return redirect(
            url_for("auth.login")
        )


    current_password = request.form.get(
        "current_password",
        ""
    )

    new_password = request.form.get(
        "new_password",
        ""
    )

    confirm_password = request.form.get(
        "confirm_password",
        ""
    )


    if not check_password_hash(
        user.password_hash,
        current_password
    ):

        flash(
            "Current password is incorrect.",
            "danger"
        )

        return redirect(
            url_for(
                "main.profile",
                section="profile"
            )
        )


    if len(new_password) < 8:

        flash(
            "New password must contain at least 8 characters.",
            "warning"
        )

        return redirect(
            url_for(
                "main.profile",
                section="profile"
            )
        )


    if new_password != confirm_password:

        flash(
            "New passwords do not match.",
            "warning"
        )

        return redirect(
            url_for(
                "main.profile",
                section="profile"
            )
        )


    user.password_hash = (
        generate_password_hash(
            new_password
        )
    )


    db.session.commit()


    flash(
        "Password changed successfully.",
        "success"
    )


    return redirect(
        url_for(
            "main.profile",
            section="profile"
        )
    )


# =========================================================
# ADD ADDRESS
# =========================================================

@main_bp.route(
    "/profile/address/add",
    methods=["POST"]
)
def add_profile_address():

    user_id = session.get("user_id")

    if not user_id:

        return redirect(
            url_for("auth.login")
        )


    full_name = request.form.get(
        "full_name",
        ""
    ).strip()

    phone = request.form.get(
        "phone",
        ""
    ).strip()

    address_line = request.form.get(
        "address_line",
        ""
    ).strip()

    city = request.form.get(
        "city",
        ""
    ).strip()

    state = request.form.get(
        "state",
        ""
    ).strip()

    pincode = request.form.get(
        "pincode",
        ""
    ).strip()


    if not all([
        full_name,
        phone,
        address_line,
        city,
        state,
        pincode
    ]):

        flash(
            "Please complete all address fields.",
            "warning"
        )

        return redirect(
            url_for(
                "main.profile",
                section="addresses"
            )
        )


    existing_count = (
        Address.query
        .filter_by(user_id=user_id)
        .count()
    )


    address = Address(

        user_id=user_id,

        full_name=full_name,

        phone=phone,

        address_line=address_line,

        city=city,

        state=state,

        pincode=pincode,

        is_default=(
            existing_count == 0
        )
    )


    db.session.add(address)

    db.session.commit()


    flash(
        "Address saved successfully.",
        "success"
    )


    return redirect(
        url_for(
            "main.profile",
            section="addresses"
        )
    )


# =========================================================
# EDIT ADDRESS
# =========================================================

@main_bp.route(
    "/profile/address/<int:address_id>/edit",
    methods=["POST"]
)
def edit_profile_address(address_id):

    user_id = session.get("user_id")


    if not user_id:

        return redirect(
            url_for("auth.login")
        )


    address = (
        Address.query
        .filter_by(
            id=address_id,
            user_id=user_id
        )
        .first()
    )


    if not address:

        flash(
            "Address not found.",
            "danger"
        )

        return redirect(
            url_for(
                "main.profile",
                section="addresses"
            )
        )


    address.full_name = request.form.get(
        "full_name",
        ""
    ).strip()

    address.phone = request.form.get(
        "phone",
        ""
    ).strip()

    address.address_line = request.form.get(
        "address_line",
        ""
    ).strip()

    address.city = request.form.get(
        "city",
        ""
    ).strip()

    address.state = request.form.get(
        "state",
        ""
    ).strip()

    address.pincode = request.form.get(
        "pincode",
        ""
    ).strip()


    db.session.commit()


    flash(
        "Address updated successfully.",
        "success"
    )


    return redirect(
        url_for(
            "main.profile",
            section="addresses"
        )
    )


# =========================================================
# DELETE ADDRESS
# =========================================================

@main_bp.route(
    "/profile/address/<int:address_id>/delete",
    methods=["POST"]
)
def delete_profile_address(address_id):

    user_id = session.get("user_id")


    if not user_id:

        return redirect(
            url_for("auth.login")
        )


    address = (
        Address.query
        .filter_by(
            id=address_id,
            user_id=user_id
        )
        .first()
    )


    if not address:

        flash(
            "Address not found.",
            "danger"
        )

        return redirect(
            url_for(
                "main.profile",
                section="addresses"
            )
        )


    was_default = address.is_default


    db.session.delete(address)

    db.session.flush()


    # -----------------------------------------------------
    # IF DEFAULT ADDRESS WAS DELETED,
    # MAKE THE MOST RECENT REMAINING ADDRESS DEFAULT
    # -----------------------------------------------------

    if was_default:

        next_address = (
            Address.query
            .filter_by(user_id=user_id)
            .order_by(
                Address.created_at.desc()
            )
            .first()
        )


        if next_address:

            next_address.is_default = True


    db.session.commit()


    flash(
        "Address deleted successfully.",
        "success"
    )


    return redirect(
        url_for(
            "main.profile",
            section="addresses"
        )
    )


# =========================================================
# SET DEFAULT ADDRESS
# =========================================================

@main_bp.route(
    "/profile/address/<int:address_id>/default",
    methods=["POST"]
)
def set_default_address(address_id):

    user_id = session.get("user_id")


    if not user_id:

        return redirect(
            url_for("auth.login")
        )


    address = (
        Address.query
        .filter_by(
            id=address_id,
            user_id=user_id
        )
        .first()
    )


    if not address:

        flash(
            "Address not found.",
            "danger"
        )

        return redirect(
            url_for(
                "main.profile",
                section="addresses"
            )
        )


    Address.query.filter_by(
        user_id=user_id
    ).update(
        {
            Address.is_default: False
        }
    )


    address.is_default = True


    db.session.commit()


    flash(
        "Default address updated.",
        "success"
    )


    return redirect(
        url_for(
            "main.profile",
            section="addresses"
        )
    )


# =========================================================
# PROJECT INFORMATION PAGES
# =========================================================

@main_bp.route("/privacy-policy")
def privacy_policy():

    return render_template(
        "privacy_policy.html"
    )


@main_bp.route("/terms-and-conditions")
def terms_conditions():

    return render_template(
        "terms_conditions.html"
    )

# =========================================================
# TRAFFIC TRACKING
# =========================================================

@main_bp.route(
    "/track-traffic",
    methods=["POST"]
)
@csrf.exempt
def track_traffic():

    # -----------------------------------------------------
    # READ JSON DATA
    # -----------------------------------------------------

    data = request.get_json(
        silent=True
    ) or {}


    visitor_id = str(
        data.get(
            "visitor_id",
            ""
        )
    ).strip()

    session_id = str(
        data.get(
            "session_id",
            ""
        )
    ).strip()

    event_type = str(
        data.get(
            "event_type",
            ""
        )
    ).strip()

    page = str(
        data.get(
            "page",
            ""
        )
    ).strip()


    # -----------------------------------------------------
    # BASIC VALIDATION
    # -----------------------------------------------------

    if not visitor_id or not session_id or not event_type:

        return {
            "success": False
        }, 400


    # -----------------------------------------------------
    # ALLOWED EVENT TYPES
    #
    # We keep this limited so random values cannot be
    # stored in the analytics table.
    # -----------------------------------------------------

    allowed_events = {
        "page_view",
        "product_view",
        "category_view",
        "subcategory_view",
        "activity"
    }


    if event_type not in allowed_events:

        return {
            "success": False
        }, 400


    # -----------------------------------------------------
    # CURRENT LOGGED-IN USER
    #
    # Guest users will have user_id = None.
    # -----------------------------------------------------

    user_id = session.get(
        "user_id"
    )


    # -----------------------------------------------------
    # RESOLVE ENTITY IDS FROM CURRENT PAGE
    #
    # Customer pages do not need to send database IDs.
    # We resolve them here from the URL.
    # -----------------------------------------------------

    product_id = None
    category_id = None
    subcategory_id = None


    try:

        from urllib.parse import (
            urlparse,
            parse_qs
        )

        parsed_url = urlparse(
            page
        )

        path = parsed_url.path

        query_params = parse_qs(
            parsed_url.query
        )


        # -------------------------------------------------
        # PRODUCT DETAIL
        #
        # Example:
        # /products/iphone-15
        # -------------------------------------------------

        if (
            event_type == "product_view"
            and path.startswith("/products/")
        ):

            product_slug = (
                path.split(
                    "/products/",
                    1
                )[1]
            )


            product = (
                Product.query
                .filter_by(
                    slug=product_slug,
                    is_active=True
                )
                .first()
            )


            if product:

                product_id = product.id

                category_id = (
                    product.category_id
                )

                subcategory_id = (
                    product.subcategory_id
                )


        # -------------------------------------------------
        # CATEGORY VIEW
        #
        # Example:
        # /products?category=electronics
        # -------------------------------------------------

        elif (
            event_type == "category_view"
            and path == "/products"
        ):

            category_slug = (
                query_params
                .get(
                    "category",
                    [None]
                )[0]
            )


            if category_slug:

                category = (
                    Category.query
                    .filter_by(
                        slug=category_slug,
                        is_active=True
                    )
                    .first()
                )


                if category:

                    category_id = category.id


        # -------------------------------------------------
        # SUBCATEGORY VIEW
        #
        # Example:
        # /products?category=electronics
        # &subcategory=shirts
        # -------------------------------------------------

        elif (
            event_type == "subcategory_view"
            and path == "/products"
        ):

            category_slug = (
                query_params
                .get(
                    "category",
                    [None]
                )[0]
            )

            subcategory_slug = (
                query_params
                .get(
                    "subcategory",
                    [None]
                )[0]
            )


            if subcategory_slug:

                subcategory = (
                    Subcategory.query
                    .filter_by(
                        slug=subcategory_slug,
                        is_active=True
                    )
                    .first()
                )


                if subcategory:

                    subcategory_id = (
                        subcategory.id
                    )

                    category_id = (
                        subcategory.category_id
                    )


    except Exception:

        current_app.logger.exception(
            "TRAFFIC ENTITY RESOLUTION FAILED"
        )


    # -----------------------------------------------------
    # CREATE EVENT
    # -----------------------------------------------------

    traffic_event = TrafficEvent(

        visitor_id=visitor_id,

        user_id=user_id,

        session_id=session_id,

        event_type=event_type,

        page=page[:255],

        product_id=product_id,

        category_id=category_id,

        subcategory_id=subcategory_id
    )


    db.session.add(
        traffic_event
    )


    try:

        db.session.commit()

    except Exception:

        db.session.rollback()

        current_app.logger.exception(
            "TRAFFIC EVENT FAILED"
        )

        return {
            "success": False
        }, 500


    return {
        "success": True
    }, 200