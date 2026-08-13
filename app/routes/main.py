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
from app import db

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
    OrderItem
)

from decimal import Decimal
from datetime import datetime
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
        addresses=addresses
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

        order = Order(
            user_id=user_id,
            order_number=order_number,

            subtotal=subtotal,
            delivery_fee=delivery_fee,
            total_amount=total_amount,

            # Payment is not implemented yet.
            # Existing database requires COD.
            payment_method="COD",

            status="CONFIRMED",

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