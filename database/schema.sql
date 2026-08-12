CREATE DATABASE IF NOT EXISTS shopease
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE shopease;


-- =========================================================
-- USERS
-- =========================================================

CREATE TABLE users (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    phone VARCHAR(20) NOT NULL UNIQUE,

    password_hash VARCHAR(255) NOT NULL,

    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_users_email (email),
    INDEX idx_users_phone (phone)
);


-- =========================================================
-- ADDRESSES
-- =========================================================

CREATE TABLE addresses (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    user_id BIGINT UNSIGNED NOT NULL,

    full_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,

    address_line VARCHAR(255) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    pincode VARCHAR(10) NOT NULL,

    is_default BOOLEAN NOT NULL DEFAULT FALSE,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_addresses_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    INDEX idx_addresses_user (user_id)
);


-- =========================================================
-- CATEGORIES
-- =========================================================

CREATE TABLE categories (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    name VARCHAR(100) NOT NULL UNIQUE,
    slug VARCHAR(120) NOT NULL UNIQUE,

    image_key VARCHAR(500) NULL,

    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP
);


-- =========================================================
-- SUBCATEGORIES
-- =========================================================

CREATE TABLE subcategories (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    category_id BIGINT UNSIGNED NOT NULL,

    name VARCHAR(100) NOT NULL,
    slug VARCHAR(120) NOT NULL,

    image_key VARCHAR(500) NULL,

    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_subcategories_category
        FOREIGN KEY (category_id)
        REFERENCES categories(id)
        ON DELETE RESTRICT,

    UNIQUE KEY uq_subcategory_category_slug (category_id, slug),

    INDEX idx_subcategories_category (category_id)
);


-- =========================================================
-- BRANDS
-- =========================================================

CREATE TABLE brands (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    name VARCHAR(100) NOT NULL UNIQUE,
    slug VARCHAR(120) NOT NULL UNIQUE,

    logo_key VARCHAR(500) NULL,

    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP
);


-- =========================================================
-- PRODUCTS
-- =========================================================

CREATE TABLE products (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    category_id BIGINT UNSIGNED NOT NULL,
    subcategory_id BIGINT UNSIGNED NULL,
    brand_id BIGINT UNSIGNED NULL,

    sku VARCHAR(50) NOT NULL UNIQUE,

    name VARCHAR(200) NOT NULL,
    slug VARCHAR(220) NOT NULL UNIQUE,

    description TEXT NULL,
    specifications JSON NULL,

    price DECIMAL(12,2) NOT NULL,
    stock_quantity INT UNSIGNED NOT NULL DEFAULT 0,

    featured BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_products_category
        FOREIGN KEY (category_id)
        REFERENCES categories(id)
        ON DELETE RESTRICT,

    CONSTRAINT fk_products_subcategory
        FOREIGN KEY (subcategory_id)
        REFERENCES subcategories(id)
        ON DELETE SET NULL,

    CONSTRAINT fk_products_brand
        FOREIGN KEY (brand_id)
        REFERENCES brands(id)
        ON DELETE SET NULL,

    CONSTRAINT chk_products_price
        CHECK (price >= 0),

    INDEX idx_products_category (category_id),
    INDEX idx_products_subcategory (subcategory_id),
    INDEX idx_products_brand (brand_id),
    INDEX idx_products_price (price),
    INDEX idx_products_stock (stock_quantity),
    INDEX idx_products_featured (featured),
    INDEX idx_products_active (is_active)
);


-- =========================================================
-- PRODUCT IMAGES
-- =========================================================

CREATE TABLE product_images (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    product_id BIGINT UNSIGNED NOT NULL,

    image_key VARCHAR(500) NOT NULL,

    alt_text VARCHAR(255) NULL,

    display_order INT UNSIGNED NOT NULL DEFAULT 0,

    is_primary BOOLEAN NOT NULL DEFAULT FALSE,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_product_images_product
        FOREIGN KEY (product_id)
        REFERENCES products(id)
        ON DELETE CASCADE,

    INDEX idx_product_images_product (product_id),
    INDEX idx_product_images_order (product_id, display_order)
);


-- =========================================================
-- WISHLIST
-- =========================================================

CREATE TABLE wishlist (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    user_id BIGINT UNSIGNED NOT NULL,
    product_id BIGINT UNSIGNED NOT NULL,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_wishlist_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_wishlist_product
        FOREIGN KEY (product_id)
        REFERENCES products(id)
        ON DELETE CASCADE,

    UNIQUE KEY uq_wishlist_user_product (user_id, product_id),

    INDEX idx_wishlist_user (user_id)
);


-- =========================================================
-- CART ITEMS
-- =========================================================

CREATE TABLE cart_items (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    user_id BIGINT UNSIGNED NOT NULL,
    product_id BIGINT UNSIGNED NOT NULL,

    quantity INT UNSIGNED NOT NULL DEFAULT 1,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_cart_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_cart_product
        FOREIGN KEY (product_id)
        REFERENCES products(id)
        ON DELETE CASCADE,

    UNIQUE KEY uq_cart_user_product (user_id, product_id),

    CONSTRAINT chk_cart_quantity
        CHECK (quantity > 0),

    INDEX idx_cart_user (user_id)
);


-- =========================================================
-- RECENTLY VIEWED PRODUCTS
-- =========================================================

CREATE TABLE recently_viewed (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    user_id BIGINT UNSIGNED NOT NULL,
    product_id BIGINT UNSIGNED NOT NULL,

    viewed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_recently_viewed_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_recently_viewed_product
        FOREIGN KEY (product_id)
        REFERENCES products(id)
        ON DELETE CASCADE,

    UNIQUE KEY uq_recently_viewed_user_product (user_id, product_id),

    INDEX idx_recently_viewed_user_date (user_id, viewed_at)
);


-- =========================================================
-- ORDERS
-- =========================================================

CREATE TABLE orders (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    user_id BIGINT UNSIGNED NOT NULL,

    order_number VARCHAR(30) NOT NULL UNIQUE,

    subtotal DECIMAL(12,2) NOT NULL,
    total_amount DECIMAL(12,2) NOT NULL,

    payment_method ENUM('COD') NOT NULL DEFAULT 'COD',

    status ENUM(
        'PENDING',
        'CONFIRMED',
        'PACKED',
        'SHIPPED',
        'DELIVERED',
        'CANCELLED'
    ) NOT NULL DEFAULT 'PENDING',

    cancellation_requested BOOLEAN NOT NULL DEFAULT FALSE,
    cancellation_reason VARCHAR(500) NULL,
    cancellation_requested_at TIMESTAMP NULL,

    cancellation_approved_at TIMESTAMP NULL,

    -- Address snapshot
    shipping_full_name VARCHAR(100) NOT NULL,
    shipping_phone VARCHAR(20) NOT NULL,
    shipping_address_line VARCHAR(255) NOT NULL,
    shipping_city VARCHAR(100) NOT NULL,
    shipping_state VARCHAR(100) NOT NULL,
    shipping_pincode VARCHAR(10) NOT NULL,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_orders_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE RESTRICT,

    CONSTRAINT chk_orders_subtotal
        CHECK (subtotal >= 0),

    CONSTRAINT chk_orders_total
        CHECK (total_amount >= 0),

    INDEX idx_orders_user (user_id),
    INDEX idx_orders_status (status),
    INDEX idx_orders_created (created_at)
);


-- =========================================================
-- ORDER ITEMS
-- =========================================================

CREATE TABLE order_items (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    order_id BIGINT UNSIGNED NOT NULL,
    product_id BIGINT UNSIGNED NULL,

    product_name VARCHAR(200) NOT NULL,
    sku VARCHAR(50) NOT NULL,

    quantity INT UNSIGNED NOT NULL,

    unit_price DECIMAL(12,2) NOT NULL,
    total_price DECIMAL(12,2) NOT NULL,

    CONSTRAINT fk_order_items_order
        FOREIGN KEY (order_id)
        REFERENCES orders(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_order_items_product
        FOREIGN KEY (product_id)
        REFERENCES products(id)
        ON DELETE SET NULL,

    CONSTRAINT chk_order_items_quantity
        CHECK (quantity > 0),

    CONSTRAINT chk_order_items_price
        CHECK (unit_price >= 0),

    INDEX idx_order_items_order (order_id),
    INDEX idx_order_items_product (product_id)
);


-- =========================================================
-- ADMINS
-- =========================================================

CREATE TABLE admins (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    full_name VARCHAR(100) NOT NULL,

    email VARCHAR(150) NOT NULL UNIQUE,

    password_hash VARCHAR(255) NOT NULL,

    role ENUM('SUPER_ADMIN', 'ADMIN') NOT NULL DEFAULT 'ADMIN',

    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_admins_email (email)
);


-- =========================================================
-- HOMEPAGE BANNERS
-- =========================================================

CREATE TABLE banners (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    title VARCHAR(200) NULL,
    description VARCHAR(500) NULL,

    image_key VARCHAR(500) NOT NULL,

    button_text VARCHAR(100) NULL,
    button_link VARCHAR(500) NULL,

    display_order INT UNSIGNED NOT NULL DEFAULT 0,

    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_banners_active_order (is_active, display_order)
);


-- =========================================================
-- WEBSITE SETTINGS
-- =========================================================

CREATE TABLE settings (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    setting_key VARCHAR(100) NOT NULL UNIQUE,
    setting_value TEXT NULL,

    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP
);


-- =========================================================
-- ADMIN ACTIVITY LOGS
-- =========================================================

CREATE TABLE activity_logs (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    admin_id BIGINT UNSIGNED NULL,

    action VARCHAR(100) NOT NULL,
    description VARCHAR(500) NULL,

    entity_type VARCHAR(100) NULL,
    entity_id BIGINT UNSIGNED NULL,

    ip_address VARCHAR(45) NULL,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_activity_logs_admin
        FOREIGN KEY (admin_id)
        REFERENCES admins(id)
        ON DELETE SET NULL,

    INDEX idx_activity_logs_admin (admin_id),
    INDEX idx_activity_logs_action (action),
    INDEX idx_activity_logs_created (created_at)
);

CREATE TABLE product_sizes (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    product_id BIGINT UNSIGNED NOT NULL,

    size VARCHAR(50) NOT NULL,

    quantity INT UNSIGNED NOT NULL DEFAULT 0,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_product_sizes_product
        FOREIGN KEY (product_id)
        REFERENCES products(id)
        ON DELETE CASCADE,

    UNIQUE KEY uq_product_size (product_id, size),

    INDEX idx_product_sizes_product (product_id)
);


ALTER TABLE cart_items
ADD COLUMN product_size_id BIGINT UNSIGNED NULL AFTER product_id;

ALTER TABLE cart_items
ADD COLUMN cart_key VARCHAR(100)
GENERATED ALWAYS AS (
    CONCAT(
        product_id,
        '-',
        COALESCE(product_size_id, 0)
    )
) STORED;

ALTER TABLE cart_items
DROP INDEX uq_cart_user_product;

ALTER TABLE cart_items
ADD UNIQUE KEY uq_cart_user_variant (
    user_id,
    cart_key
);

ALTER TABLE cart_items
ADD CONSTRAINT fk_cart_product_size
FOREIGN KEY (product_size_id)
REFERENCES product_sizes(id)
ON DELETE CASCADE;