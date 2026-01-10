-- Enable Foreign Keys
PRAGMA foreign_keys = ON;

-- ==========================================
-- 1. Users & Authentication
-- ==========================================

CREATE TABLE roles (
    role_id INTEGER PRIMARY KEY AUTOINCREMENT,
    role_name TEXT NOT NULL UNIQUE,
    description TEXT
);

CREATE TABLE users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES roles(role_id)
);

CREATE TABLE user_addresses (
    address_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    address_line1 TEXT NOT NULL,
    city TEXT NOT NULL,
    postal_code TEXT NOT NULL,
    country TEXT NOT NULL,
    is_default BOOLEAN DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- ==========================================
-- 2. Catalog (Products, Categories, Brands)
-- ==========================================

CREATE TABLE categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    parent_id INTEGER,
    name TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,
    FOREIGN KEY (parent_id) REFERENCES categories(category_id)
);

CREATE TABLE brands (
    brand_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    website TEXT
);

CREATE TABLE products (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER,
    brand_id INTEGER,
    title TEXT NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    sku TEXT UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(category_id),
    FOREIGN KEY (brand_id) REFERENCES brands(brand_id)
);

CREATE TABLE product_attributes (
    attribute_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER,
    attribute_name TEXT NOT NULL, -- e.g., "Color", "Size"
    attribute_value TEXT NOT NULL, -- e.g., "Red", "XL"
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

CREATE TABLE product_images (
    image_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER,
    image_url TEXT NOT NULL,
    is_primary BOOLEAN DEFAULT 0,
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

CREATE TABLE inventory (
    inventory_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER UNIQUE,
    quantity_in_stock INTEGER DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- ==========================================
-- 3. Engagement (Reviews, Wishlists)
-- ==========================================

CREATE TABLE reviews (
    review_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER,
    user_id INTEGER,
    rating INTEGER CHECK(rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE wishlists (
    wishlist_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    name TEXT DEFAULT 'My Wishlist',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE wishlist_items (
    wishlist_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    wishlist_id INTEGER,
    product_id INTEGER,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (wishlist_id) REFERENCES wishlists(wishlist_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

CREATE TABLE coupons (
    coupon_id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL UNIQUE,
    discount_percent DECIMAL(5, 2),
    valid_until TIMESTAMP,
    is_active BOOLEAN DEFAULT 1
);

-- ==========================================
-- 4. Sales & Orders
-- ==========================================

CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    coupon_id INTEGER,
    total_amount DECIMAL(10, 2) NOT NULL,
    status TEXT DEFAULT 'pending', -- pending, paid, shipped, delivered, cancelled
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (coupon_id) REFERENCES coupons(coupon_id)
);

CREATE TABLE order_items (
    order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER,
    product_id INTEGER,
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

CREATE TABLE order_status_history (
    history_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER,
    status TEXT NOT NULL,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);

CREATE TABLE invoices (
    invoice_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER UNIQUE,
    invoice_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    pdf_url TEXT,
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);

CREATE TABLE payments (
    payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER,
    payment_method TEXT NOT NULL, -- credit_card, paypal, bank_transfer
    amount DECIMAL(10, 2) NOT NULL,
    status TEXT DEFAULT 'success',
    transaction_id TEXT,
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);

-- ==========================================
-- 5. Logistics
-- ==========================================

CREATE TABLE carriers (
    carrier_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL, -- DHL, FedEx, UPS
    contact_number TEXT
);

CREATE TABLE shipments (
    shipment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER,
    carrier_id INTEGER,
    tracking_number TEXT,
    shipped_date TIMESTAMP,
    estimated_delivery TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (carrier_id) REFERENCES carriers(carrier_id)
);

-- ==========================================
-- Seed Data
-- ==========================================

INSERT INTO roles (role_name) VALUES ('admin'), ('customer');

INSERT INTO users (username, email, password_hash, role_id) VALUES 
('alice', 'alice@example.com', 'hash123', 2),
('bob', 'bob@example.com', 'hash456', 2),
('admin', 'admin@store.com', 'admin789', 1);

INSERT INTO categories (name, slug) VALUES 
('Electronics', 'electronics'),
('Laptops', 'laptops'),
('Smartphones', 'smartphones'),
('Accessories', 'accessories');

INSERT INTO brands (name) VALUES ('Apple'), ('Samsung'), ('Sony'), ('Dell');

INSERT INTO products (category_id, brand_id, title, description, price, sku) VALUES 
(3, 1, 'iPhone 15 Pro', 'Latest Apple smartphone', 999.00, 'IP15P-128'),
(3, 2, 'Galaxy S24', 'Samsung flagship', 899.00, 'S24-256'),
(2, 4, 'XPS 13', 'Dell ultrabook', 1200.00, 'DELL-XPS13'),
(4, 3, 'WH-1000XM5', 'Sony Noise Cancelling Headphones', 349.00, 'SONY-XM5');

INSERT INTO inventory (product_id, quantity_in_stock) VALUES (1, 50), (2, 30), (3, 10), (4, 100);

INSERT INTO orders (user_id, total_amount, status) VALUES 
(1, 999.00, 'delivered'),
(2, 349.00, 'shipped');

INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES 
(1, 1, 1, 999.00),
(2, 4, 1, 349.00);

INSERT INTO reviews (product_id, user_id, rating, comment) VALUES 
(1, 1, 5, 'Love the titanium finish!'),
(4, 2, 4, 'Great sound, but a bit pricey.');
