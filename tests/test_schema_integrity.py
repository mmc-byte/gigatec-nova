import pytest
from mysql.connector import IntegrityError
from mysql.connector import DatabaseError

from app.db.connection import get_connection

# =====================================================
# TESTS DE INTEGRIDAD DEL ESQUEMA DE LA DB
# =====================================================

# I. Obtener conexión
@pytest.fixture
def connection():
    conn = get_connection()
    conn.start_transaction()

    yield conn

    conn.rollback()
    conn.close()

# =====================================================
# II. Tests críticos
# =====================================================

def test_product_sku_must_be_unique(connection):
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO brands (name, active)
        VALUES ('Test Brand', TRUE)
    """)
    brand_id = cursor.lastrowid

    cursor.execute("""
        INSERT INTO categories (name, description, active)
        VALUES ('Test Category', 'Test category', TRUE)
    """)
    category_id = cursor.lastrowid

    cursor.execute("""
        INSERT INTO products
            (brand_id, category_id, name, description, sku, price, active)
        VALUES
            (%s, %s, 'Product A', 'Test product', 'TEST-SKU-001', 100.00, TRUE)
    """, (brand_id, category_id))

    with pytest.raises(IntegrityError):
        cursor.execute("""
            INSERT INTO products
                (brand_id, category_id, name, description, sku, price, active)
            VALUES
                (%s, %s, 'Product B', 'Test product', 'TEST-SKU-001', 200.00, TRUE)
        """, (brand_id, category_id))

    cursor.close()

# =====================================================

def test_customer_email_must_be_unique(connection):
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO customers
            (first_name, last_name, email, active)
        VALUES
            ('Test', 'Customer', 'test@example.com', TRUE)
    """)

    with pytest.raises(IntegrityError):
        cursor.execute("""
            INSERT INTO customers
                (first_name, last_name, email, active)
            VALUES
                ('Another', 'Customer', 'test@example.com', TRUE)
        """)

    cursor.close()

# =====================================================

def test_inventory_quantity_cannot_be_negative(connection):
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO brands (name, active)
        VALUES ('Inventory Brand', TRUE)
    """)
    brand_id = cursor.lastrowid

    cursor.execute("""
        INSERT INTO categories (name, description, active)
        VALUES ('Inventory Category', 'Test category', TRUE)
    """)
    category_id = cursor.lastrowid

    cursor.execute("""
        INSERT INTO products
            (brand_id, category_id, name, description, sku, price, active)
        VALUES
            (%s, %s, 'Inventory Product', 'Test product',
             'INV-TEST-001', 100.00, TRUE)
    """, (brand_id, category_id))
    product_id = cursor.lastrowid

    # with pytest.raises(IntegrityError):
    #     cursor.execute("""
    #         INSERT INTO inventory (product_id, quantity)
    #         VALUES (%s, -1)
    #     """, (product_id,))
    with pytest.raises(DatabaseError):
        cursor.execute("""
            INSERT INTO inventory (product_id, quantity)
            VALUES (%s, -1)
        """, (product_id,))

    cursor.close()
# =====================================================

def test_order_item_quantity_must_be_positive(connection):
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO customers
            (first_name, last_name, email, active)
        VALUES
            ('Order', 'Customer', 'order@example.com', TRUE)
    """)
    customer_id = cursor.lastrowid

    cursor.execute("""
        INSERT INTO orders
            (customer_id, status, subtotal, tax_rate, tax_amount, total_amount,
            shipping_address_line_1,
            shipping_city,
            shipping_region_or_state,
            shipping_postal_code,
            shipping_country
            )
        VALUES
            (%s, 'pending', 100.00, 18.00, 18.00, 118.00, 
            '123 Test St', 'Test City', 'Test State', '12345', 'Test Country')
    """, (customer_id,))
    order_id = cursor.lastrowid

    cursor.execute("""
        INSERT INTO brands (name, active)
        VALUES ('Order Brand', TRUE)
    """)
    brand_id = cursor.lastrowid

    cursor.execute("""
        INSERT INTO categories (name, description, active)
        VALUES ('Order Category', 'Test category', TRUE)
    """)
    category_id = cursor.lastrowid

    cursor.execute("""
        INSERT INTO products
            (brand_id, category_id, name, description, sku, price, active)
        VALUES
            (%s, %s, 'Order Product', 'Test product',
             'ORDER-TEST-001', 100.00, TRUE)
    """, (brand_id, category_id))
    product_id = cursor.lastrowid

    with pytest.raises(DatabaseError):
        cursor.execute("""
            INSERT INTO order_items
                (order_id, product_id, quantity, unit_price)
            VALUES
                (%s, %s, 0, 100.00)
        """, (order_id, product_id))
   

    cursor.close()

# =====================================================

def test_order_item_product_cannot_be_repeated(connection):
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO customers
            (first_name, last_name, email, active)
        VALUES
            ('Duplicate', 'Test', 'duplicate@example.com', TRUE)
    """)
    customer_id = cursor.lastrowid

    cursor.execute("""
        INSERT INTO orders
            (customer_id, status, subtotal, tax_rate, tax_amount, total_amount,
            shipping_address_line_1,
            shipping_city,
            shipping_region_or_state,
            shipping_postal_code,
            shipping_country
            )
        VALUES
            (%s, 'pending', 200.00, 18.00, 36.00, 236.00, 
            '123 Test St', 'Test City', 'Test State', '12345', 'Test Country')
    """, (customer_id,))
    order_id = cursor.lastrowid

    cursor.execute("""
        INSERT INTO brands (name, active)
        VALUES ('Duplicate Brand', TRUE)
    """)
    brand_id = cursor.lastrowid

    cursor.execute("""
        INSERT INTO categories (name, description, active)
        VALUES ('Duplicate Category', 'Test category', TRUE)
    """)
    category_id = cursor.lastrowid

    cursor.execute("""
        INSERT INTO products
            (brand_id, category_id, name, description, sku, price, active)
        VALUES
            (%s, %s, 'Duplicate Product', 'Test product',
             'DUP-TEST-001', 100.00, TRUE)
    """, (brand_id, category_id))
    product_id = cursor.lastrowid

    cursor.execute("""
        INSERT INTO order_items
            (order_id, product_id, quantity, unit_price)
        VALUES
            (%s, %s, 1, 100.00)
    """, (order_id, product_id))

    with pytest.raises(IntegrityError):
        cursor.execute("""
            INSERT INTO order_items
                (order_id, product_id, quantity, unit_price)
            VALUES
                (%s, %s, 2, 100.00)
        """, (order_id, product_id))

    cursor.close()

# =====================================================
# III. Tests de FKs y ENUMs
# =====================================================
def test_foreign_key_order_item_invalid_order(connection):
    """
    Verifica que no se pueda crear un order_item con un order_id inexistente.
    Debe lanzar IntegrityError por violación de FK.
    """
    cursor = connection.cursor()

    # Crear datos mínimos necesarios: brand, category, product
    cursor.execute("""
        INSERT INTO brands (name, active)
        VALUES ('Test Brand FK', TRUE)
    """)
    brand_id = cursor.lastrowid

    cursor.execute("""
        INSERT INTO categories (name, description, active)
        VALUES ('Test Category FK', 'Test category', TRUE)
    """)
    category_id = cursor.lastrowid

    cursor.execute("""
        INSERT INTO products
            (brand_id, category_id, name, description, sku, price, active)
        VALUES
            (%s, %s, 'Product FK Test', 'Test product', 'TEST-SKU-FK-001', 100.00, TRUE)
    """, (brand_id, category_id))
    product_id = cursor.lastrowid

    # Intentar crear order_item con order_id inexistente (99999)
    # La FK order_items_order_id debe lanzar IntegrityError
    with pytest.raises(IntegrityError):
        cursor.execute("""
            INSERT INTO order_items (order_id, product_id, quantity, unit_price)
            VALUES (%s, %s, 1, 100.00)
        """, (99999, product_id))

    cursor.close()

def test_enum_orders_status_invalid(connection):
    """
    Verifica que no se pueda insertar un pedido con un status inválido.
    Los estados válidos son: pending, confirmed, shipped, delivered, cancelled.
    """
    cursor = connection.cursor()
    
    # Forzar modo estricto para que MySQL rechace valores ENUM inválidos
    cursor.execute("SET SESSION sql_mode = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION'")

    # Crear customer mínimo para el order
    cursor.execute("""
        INSERT INTO customers (first_name, last_name, email, active)
        VALUES ('Status', 'Test', 'status.test@example.com', TRUE)
    """)
    customer_id = cursor.lastrowid

    # Intentar insertar order con status inválido 'invalid_status'
    # MySQL debe rechazarlo por ser un valor no permitido en el ENUM
    with pytest.raises(DatabaseError) as exc_info:
        cursor.execute("""
            INSERT INTO orders (
                customer_id,
                shipping_address_line_1,
                shipping_address_line_2,
                shipping_city,
                shipping_region_or_state,
                shipping_postal_code,
                shipping_country,
                status,
                subtotal,
                tax_rate,
                tax_amount,
                total_amount
            ) VALUES (
                %s,
                '123 Main St',
                NULL,
                'Springfield',
                'IL',
                '62701',
                'USA',
                'invalid_status',
                100.00,
                0.10,
                10.00,
                110.00
            )
        """, (customer_id,))

    # Verificar que el mensaje de error mencione la restricción de ENUM
    # Diferentes mensajes según el modo SQL
    error_message = str(exc_info.value)
    assert any(phrase in error_message.lower() for phrase in [
        'invalid_status',
        'enum',
        'truncated',
        'data truncated'
    ])

    cursor.close()


def test_enum_payments_status_invalid(connection):
    """
    Verifica que no se pueda insertar un pago con un status inválido.
    Los estados válidos son: pending, completed, failed.
    """
    cursor = connection.cursor()
    
    # Forzar modo estricto para que MySQL rechace valores ENUM inválidos
    cursor.execute("SET SESSION sql_mode = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION'")

    # Crear datos mínimos: customer, brand, category, product, order
    cursor.execute("""
        INSERT INTO customers (first_name, last_name, email, active)
        VALUES ('Payment', 'Test', 'payment.test@example.com', TRUE)
    """)
    customer_id = cursor.lastrowid

    cursor.execute("""
        INSERT INTO brands (name, active)
        VALUES ('Test Brand Payment', TRUE)
    """)
    brand_id = cursor.lastrowid

    cursor.execute("""
        INSERT INTO categories (name, description, active)
        VALUES ('Test Category Payment', 'Test category', TRUE)
    """)
    category_id = cursor.lastrowid

    cursor.execute("""
        INSERT INTO products
            (brand_id, category_id, name, description, sku, price, active)
        VALUES
            (%s, %s, 'Product Payment Test', 'Test product', 'TEST-SKU-PMT-001', 100.00, TRUE)
    """, (brand_id, category_id))
    product_id = cursor.lastrowid

    # Crear order válido
    cursor.execute("""
        INSERT INTO orders (
            customer_id,
            shipping_address_line_1,
            shipping_address_line_2,
            shipping_city,
            shipping_region_or_state,
            shipping_postal_code,
            shipping_country,
            status,
            subtotal,
            tax_rate,
            tax_amount,
            total_amount
        ) VALUES (
            %s,
            '456 Elm St',
            NULL,
            'Springfield',
            'IL',
            '62702',
            'USA',
            'pending',
            100.00,
            0.10,
            10.00,
            110.00
        )
    """, (customer_id,))
    order_id = cursor.lastrowid

    # Intentar insertar payment con status inválido 'invalid_status'
    # MySQL debe rechazarlo por ser un valor no permitido en el ENUM
    with pytest.raises(DatabaseError) as exc_info:
        cursor.execute("""
            INSERT INTO payments (
                order_id,
                status,
                amount,
                payment_method,
                transaction_reference
            ) VALUES (
                %s,
                'invalid_status',
                110.00,
                'card',
                'TXN-INVALID-001'
            )
        """, (order_id,))

    # Verificar que el mensaje de error mencione la restricción de ENUM
    error_message = str(exc_info.value)
    assert any(phrase in error_message.lower() for phrase in [
        'invalid_status',
        'enum',
        'truncated',
        'data truncated'
    ])

    cursor.close()


# =====================================================
# Fin de los tests
# =====================================================