from datetime import datetime

from app import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)

    full_name = db.Column(db.String(100), nullable=False)

    email = db.Column(
        db.String(150),
        unique=True,
        nullable=False,
        index=True
    )

    phone = db.Column(
        db.String(20),
        unique=True,
        nullable=False,
        index=True
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    is_active = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    def __repr__(self):
        return f"<User {self.email}>"



class Admin(db.Model):
    __tablename__ = "admins"

    id = db.Column(
        db.BigInteger,
        primary_key=True,
        autoincrement=True
    )

    full_name = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(150),
        unique=True,
        nullable=False,
        index=True
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    role = db.Column(
        db.Enum("SUPER_ADMIN", "ADMIN"),
        nullable=False,
        default="ADMIN"
    )

    is_active = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    def __repr__(self):
        return f"<Admin {self.email}>"


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(
        db.BigInteger,
        primary_key=True,
        autoincrement=True
    )

    name = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    slug = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    image_key = db.Column(
        db.String(500),
        nullable=True
    )

    is_active = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    def __repr__(self):
        return f"<Category {self.name}>"


class Subcategory(db.Model):
    __tablename__ = "subcategories"

    id = db.Column(
        db.BigInteger,
        primary_key=True,
        autoincrement=True
    )

    category_id = db.Column(
        db.BigInteger,
        db.ForeignKey("categories.id"),
        nullable=False,
        index=True
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    slug = db.Column(
        db.String(120),
        nullable=False
    )

    image_key = db.Column(
        db.String(500),
        nullable=True
    )

    is_active = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    category = db.relationship(
        "Category",
        backref=db.backref(
            "subcategories",
            lazy=True
        )
    )

    def __repr__(self):
        return f"<Subcategory {self.name}>"


class Brand(db.Model):
    __tablename__ = "brands"

    id = db.Column(
        db.BigInteger,
        primary_key=True,
        autoincrement=True
    )

    name = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    slug = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    logo_key = db.Column(
        db.String(500),
        nullable=True
    )

    is_active = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    def __repr__(self):
        return f"<Brand {self.name}>"



# =========================================================
# PRODUCT
# =========================================================

class Product(db.Model):

    __tablename__ = "products"

    id = db.Column(
        db.BigInteger,
        primary_key=True,
        autoincrement=True
    )

    category_id = db.Column(
        db.BigInteger,
        db.ForeignKey("categories.id"),
        nullable=False
    )

    subcategory_id = db.Column(
        db.BigInteger,
        db.ForeignKey("subcategories.id"),
        nullable=True
    )

    brand_id = db.Column(
        db.BigInteger,
        db.ForeignKey("brands.id"),
        nullable=True
    )

    sku = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    name = db.Column(
        db.String(200),
        nullable=False
    )

    slug = db.Column(
        db.String(220),
        unique=True,
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=True
    )

    specifications = db.Column(
        db.JSON,
        nullable=True
    )

    price = db.Column(
        db.Numeric(12, 2),
        nullable=False
    )

    stock_quantity = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )

    featured = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    is_active = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.current_timestamp()
    )

    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp()
    )

    category = db.relationship(
        "Category",
        backref=db.backref(
            "products",
            lazy=True
        )
    )

    subcategory = db.relationship(
        "Subcategory",
        backref=db.backref(
            "products",
            lazy=True
        )
    )

    brand = db.relationship(
        "Brand",
        backref=db.backref(
            "products",
            lazy=True
        )
    )

    images = db.relationship(
        "ProductImage",
        back_populates="product",
        cascade="all, delete-orphan",
        order_by="ProductImage.display_order"
    )

    sizes = db.relationship(
        "ProductSize",
        back_populates="product",
        cascade="all, delete-orphan",
        order_by="ProductSize.id"
    )


# =========================================================
# PRODUCT SIZE / VARIANT INVENTORY
# =========================================================

class ProductSize(db.Model):

    __tablename__ = "product_sizes"

    id = db.Column(
        db.BigInteger,
        primary_key=True,
        autoincrement=True
    )

    product_id = db.Column(
        db.BigInteger,
        db.ForeignKey("products.id"),
        nullable=False,
        index=True
    )

    size = db.Column(
        db.String(50),
        nullable=False
    )

    price = db.Column(
        db.Numeric(12, 2),
        nullable=False
    )

    quantity = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )

    description = db.Column(
        db.Text,
        nullable=True
    )

    specifications = db.Column(
        db.JSON,
        nullable=True
    )
    
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.current_timestamp()
    )

    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp()
    )

    product = db.relationship(
        "Product",
        back_populates="sizes"
    )

# =========================================================
# PRODUCT IMAGE
# =========================================================

class ProductImage(db.Model):

    __tablename__ = "product_images"

    id = db.Column(
        db.BigInteger,
        primary_key=True,
        autoincrement=True
    )

    product_id = db.Column(
        db.BigInteger,
        db.ForeignKey("products.id"),
        nullable=False
    )

    image_key = db.Column(
        db.String(500),
        nullable=False
    )

    alt_text = db.Column(
        db.String(255),
        nullable=True
    )

    display_order = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )

    is_primary = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.current_timestamp()
    )

    product = db.relationship(
        "Product",
        back_populates="images"
    )

# =========================================================
# HOMEPAGE BANNER
# =========================================================

class Banner(db.Model):

    __tablename__ = "banners"

    id = db.Column(
        db.BigInteger,
        primary_key=True,
        autoincrement=True
    )

    title = db.Column(
        db.String(200),
        nullable=True
    )

    description = db.Column(
        db.String(500),
        nullable=True
    )

    image_key = db.Column(
        db.String(500),
        nullable=False
    )

    button_text = db.Column(
        db.String(100),
        nullable=True
    )

    button_link = db.Column(
        db.String(500),
        nullable=True
    )

    display_order = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )

    is_active = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.current_timestamp()
    )

    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp()
    )

# =========================================================
# CART ITEM
# =========================================================

class CartItem(db.Model):

    __tablename__ = "cart_items"

    id = db.Column(
        db.BigInteger,
        primary_key=True,
        autoincrement=True
    )

    user_id = db.Column(
        db.BigInteger,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    product_id = db.Column(
        db.BigInteger,
        db.ForeignKey("products.id"),
        nullable=False,
        index=True
    )

    product_size_id = db.Column(
        db.BigInteger,
        db.ForeignKey("product_sizes.id"),
        nullable=True,
        index=True
    )

    quantity = db.Column(
        db.Integer,
        nullable=False,
        default=1
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.current_timestamp()
    )

    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp()
    )

    user = db.relationship(
        "User",
        backref=db.backref(
            "cart_items",
            lazy=True
        )
    )

    product = db.relationship(
        "Product",
        backref=db.backref(
            "cart_items",
            lazy=True
        )
    )

    product_size = db.relationship(
        "ProductSize",
        backref=db.backref(
            "cart_items",
            lazy=True
        )
    )

    def __repr__(self):

        return (
            f"<CartItem "
            f"user={self.user_id} "
            f"product={self.product_id} "
            f"variant={self.product_size_id}>"
        )

# =========================================================
# ADDRESS
# =========================================================

class Address(db.Model):

    __tablename__ = "addresses"

    id = db.Column(
        db.BigInteger,
        primary_key=True,
        autoincrement=True
    )

    user_id = db.Column(
        db.BigInteger,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    full_name = db.Column(
        db.String(100),
        nullable=False
    )

    phone = db.Column(
        db.String(20),
        nullable=False
    )

    address_line = db.Column(
        db.String(255),
        nullable=False
    )

    city = db.Column(
        db.String(100),
        nullable=False
    )

    state = db.Column(
        db.String(100),
        nullable=False
    )

    pincode = db.Column(
        db.String(10),
        nullable=False
    )

    is_default = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.current_timestamp()
    )

    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp()
    )

    user = db.relationship(
        "User",
        backref=db.backref(
            "addresses",
            lazy=True
        )
    )


# =========================================================
# ORDER
# =========================================================

class Order(db.Model):

    __tablename__ = "orders"

    id = db.Column(
        db.BigInteger,
        primary_key=True,
        autoincrement=True
    )

    user_id = db.Column(
        db.BigInteger,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    order_number = db.Column(
        db.String(30),
        unique=True,
        nullable=False
    )

    subtotal = db.Column(
        db.Numeric(12, 2),
        nullable=False
    )

    delivery_fee = db.Column(
        db.Numeric(12, 2),
        nullable=False,
        default=0
    )

    total_amount = db.Column(
        db.Numeric(12, 2),
        nullable=False
    )

    payment_method = db.Column(
        db.Enum("COD"),
        nullable=False,
        default="COD"
    )

    status = db.Column(
        db.Enum(
            "PENDING",
            "CONFIRMED",
            "PACKED",
            "SHIPPED",
            "DELIVERED",
            "CANCELLED"
        ),
        nullable=False,
        default="PENDING",
        index=True
    )

    cancellation_requested = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    cancellation_reason = db.Column(
        db.String(500),
        nullable=True
    )

    cancellation_requested_at = db.Column(
        db.DateTime,
        nullable=True
    )

    cancellation_approved_at = db.Column(
        db.DateTime,
        nullable=True
    )

    shipping_full_name = db.Column(
        db.String(100),
        nullable=False
    )

    shipping_phone = db.Column(
        db.String(20),
        nullable=False
    )

    shipping_email = db.Column(
        db.String(150),
        nullable=False
    )

    shipping_address_line = db.Column(
        db.String(255),
        nullable=False
    )

    shipping_city = db.Column(
        db.String(100),
        nullable=False
    )

    shipping_state = db.Column(
        db.String(100),
        nullable=False
    )

    shipping_pincode = db.Column(
        db.String(10),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.current_timestamp(),
        index=True
    )

    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp()
    )

    user = db.relationship(
        "User",
        backref=db.backref(
            "orders",
            lazy=True
        )
    )

    items = db.relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan"
    )


# =========================================================
# ORDER ITEM
# =========================================================

class OrderItem(db.Model):

    __tablename__ = "order_items"

    id = db.Column(
        db.BigInteger,
        primary_key=True,
        autoincrement=True
    )

    order_id = db.Column(
        db.BigInteger,
        db.ForeignKey("orders.id"),
        nullable=False,
        index=True
    )

    product_id = db.Column(
        db.BigInteger,
        db.ForeignKey("products.id"),
        nullable=True,
        index=True
    )

    product_size_id = db.Column(
        db.BigInteger,
        db.ForeignKey("product_sizes.id"),
        nullable=True,
        index=True
    )

    product_name = db.Column(
        db.String(200),
        nullable=False
    )

    sku = db.Column(
        db.String(50),
        nullable=False
    )

    variant_name = db.Column(
        db.String(100),
        nullable=True
    )

    quantity = db.Column(
        db.Integer,
        nullable=False
    )

    unit_price = db.Column(
        db.Numeric(12, 2),
        nullable=False
    )

    total_price = db.Column(
        db.Numeric(12, 2),
        nullable=False
    )

    order = db.relationship(
        "Order",
        back_populates="items"
    )

    product = db.relationship(
        "Product",
        backref=db.backref(
            "order_items",
            lazy=True
        )
    )

    product_size = db.relationship(
        "ProductSize",
        backref=db.backref(
            "order_items",
            lazy=True
        )
    )