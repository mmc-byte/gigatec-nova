-- =====================================================
-- Gigatec Nova - Primer esquema
-- MySQL 8.0+
-- =====================================================

-- Charset y collation
SET NAMES utf8mb4;
SET character_set_client = utf8mb4;
SET character_set_connection = utf8mb4;
SET collation_connection = utf8mb4_0900_ai_ci;

-- =====================================================
-- Eliminar tablas 
-- orden inverso para evitar errores de FK
-- =====================================================
DROP TABLE IF EXISTS shipments;
DROP TABLE IF EXISTS payments;
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS inventory;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS brands;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS addresses;
DROP TABLE IF EXISTS customers;

-- =====================================================
-- I. Tabla: customers
-- =====================================================
CREATE TABLE customers (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    UNIQUE KEY uk_customers_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- =====================================================
-- II. Tabla: addresses
-- =====================================================
CREATE TABLE addresses (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    customer_id BIGINT UNSIGNED NOT NULL,
    address_line_1 VARCHAR(255) NOT NULL,
    address_line_2 VARCHAR(255) NULL,
    city VARCHAR(100) NOT NULL,
    region_or_state VARCHAR(100) NOT NULL,
    postal_code VARCHAR(20) NOT NULL,
    country VARCHAR(100) NOT NULL,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    CONSTRAINT fk_addresses_customer_id FOREIGN KEY (customer_id)
        REFERENCES customers(id) ON DELETE RESTRICT ON UPDATE RESTRICT,

    INDEX idx_addresses_customer_id (customer_id),
    INDEX idx_addresses_active (active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- =====================================================
-- III. Tabla: categories
-- =====================================================
CREATE TABLE categories (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT NULL,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    UNIQUE KEY uk_categories_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- =====================================================
-- IV. Tabla: brands
-- =====================================================
CREATE TABLE brands (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    UNIQUE KEY uk_brands_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- =====================================================
-- V. Tabla: products
-- =====================================================
CREATE TABLE products (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    category_id BIGINT UNSIGNED NOT NULL,
    brand_id BIGINT UNSIGNED NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT NULL,
    sku VARCHAR(50) NOT NULL,
    price DECIMAL(15,2) NOT NULL CHECK (price >= 0),
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    UNIQUE KEY uk_products_sku (sku),

    CONSTRAINT fk_products_category_id FOREIGN KEY (category_id)
        REFERENCES categories(id) ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT fk_products_brand_id FOREIGN KEY (brand_id)
        REFERENCES brands(id) ON DELETE RESTRICT ON UPDATE RESTRICT,

    INDEX idx_products_category_id (category_id),
    INDEX idx_products_brand_id (brand_id),
    INDEX idx_products_price (price),
    INDEX idx_products_active (active),
    INDEX idx_products_name (name),
    INDEX idx_products_sku (sku)  -- Para búsquedas rápidas por SKU
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- =====================================================
-- VI. Tabla: inventory (1:1 con products)
-- =====================================================
CREATE TABLE inventory (
    product_id BIGINT UNSIGNED NOT NULL,
    quantity INT NOT NULL CHECK (quantity >= 0),
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (product_id),
    CONSTRAINT fk_inventory_product_id FOREIGN KEY (product_id)
        REFERENCES products(id) ON DELETE RESTRICT ON UPDATE RESTRICT,

    INDEX idx_inventory_quantity (quantity)  -- Para consultas de stock bajo
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- =====================================================
-- VII. Tabla: orders
-- =====================================================
CREATE TABLE orders (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    customer_id BIGINT UNSIGNED NOT NULL,

    -- Snapshot histórico de la dirección de envío
    shipping_address_line_1 VARCHAR(255) NOT NULL,
    shipping_address_line_2 VARCHAR(255) NULL,
    shipping_city VARCHAR(100) NOT NULL,
    shipping_region_or_state VARCHAR(100) NOT NULL,
    shipping_postal_code VARCHAR(20) NOT NULL,
    shipping_country VARCHAR(100) NOT NULL,

    status ENUM('pending', 'confirmed', 'shipped', 'delivered', 'cancelled')
        NOT NULL DEFAULT 'pending',

    subtotal DECIMAL(15,2) NOT NULL CHECK (subtotal >= 0),
    tax_rate DECIMAL(7,4) NOT NULL CHECK (tax_rate >= 0),
    tax_amount DECIMAL(15,2) NOT NULL CHECK (tax_amount >= 0),
    total_amount DECIMAL(15,2) NOT NULL CHECK (total_amount >= 0),

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    CONSTRAINT fk_orders_customer_id FOREIGN KEY (customer_id)
        REFERENCES customers(id) ON DELETE RESTRICT ON UPDATE RESTRICT,

    INDEX idx_orders_customer_id (customer_id),
    INDEX idx_orders_status (status),
    INDEX idx_orders_created_at (created_at),
    INDEX idx_orders_customer_status (customer_id, status)  -- Para consultas de historial por estado
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- =====================================================
-- VIII. Tabla: order_items
-- =====================================================
CREATE TABLE order_items (
    order_id BIGINT UNSIGNED NOT NULL,
    product_id BIGINT UNSIGNED NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(15,2) NOT NULL CHECK (unit_price >= 0),

    PRIMARY KEY (order_id, product_id),

    CONSTRAINT fk_order_items_order_id FOREIGN KEY (order_id)
        REFERENCES orders(id) ON DELETE CASCADE ON UPDATE RESTRICT,

    CONSTRAINT fk_order_items_product_id FOREIGN KEY (product_id)
        REFERENCES products(id) ON DELETE RESTRICT ON UPDATE RESTRICT,

    INDEX idx_order_items_product_id (product_id),  -- Para análisis de productos más vendidos
    INDEX idx_order_items_order_id (order_id)       -- Para consultas JOIN con orders
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- =====================================================
-- IX. Tabla: payments
-- =====================================================
CREATE TABLE payments (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    order_id BIGINT UNSIGNED NOT NULL,
    status ENUM('pending', 'completed', 'failed') NOT NULL DEFAULT 'pending',
    amount DECIMAL(15,2) NOT NULL CHECK (amount >= 0),
    payment_method ENUM('card', 'paypal', 'bank_transfer') NOT NULL,
    transaction_reference VARCHAR(100) NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    UNIQUE KEY uk_payments_order_id (order_id),
    UNIQUE KEY uk_payments_transaction_reference (transaction_reference),

    CONSTRAINT fk_payments_order_id FOREIGN KEY (order_id)
        REFERENCES orders(id) ON DELETE RESTRICT ON UPDATE RESTRICT,

    INDEX idx_payments_status (status),
    INDEX idx_payments_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- =====================================================
-- X. Tabla: shipments
-- =====================================================
CREATE TABLE shipments (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    order_id BIGINT UNSIGNED NOT NULL,
    status ENUM('pending', 'shipped', 'delivered') NOT NULL DEFAULT 'pending',
    tracking_number VARCHAR(100) NULL,
    shipped_at TIMESTAMP NULL,
    delivered_at TIMESTAMP NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    UNIQUE KEY uk_shipments_order_id (order_id),
    UNIQUE KEY uk_shipments_tracking_number (tracking_number),

    CONSTRAINT fk_shipments_order_id FOREIGN KEY (order_id)
        REFERENCES orders(id) ON DELETE RESTRICT ON UPDATE RESTRICT,

    INDEX idx_shipments_status (status),
    INDEX idx_shipments_tracking_number (tracking_number),
    INDEX idx_shipments_shipped_at (shipped_at),
    INDEX idx_shipments_delivered_at (delivered_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- =====================================================
-- XI. Verificación rápida de tablas creadas
-- =====================================================
SHOW TABLES;

-- =====================================================
-- Fin del archivo
-- =====================================================