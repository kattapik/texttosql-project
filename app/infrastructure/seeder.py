from faker import Faker
import random
from datetime import datetime, timedelta
from app.infrastructure.sqlite_db import SqliteRepository

class DataSeeder:
    """
    Handles seeding of realistic mock data for all 19 database tables.
    Organized by Domain Area (Users, Catalog, Sales, Logistics, Engagement).
    """

    def __init__(self, db_repo: SqliteRepository):
        self.db_repo = db_repo
        self.fake = Faker()
    
    def _execute(self, sql: str):
        """Helper to execute SQL silently"""
        self.db_repo.execute_query(sql)

    def _get_ids(self, table_name: str, id_col: str) -> list:
        """Helper to fetch all IDs from a table"""
        res = self.db_repo.execute_query(f"SELECT {id_col} FROM {table_name}")
        if res.success and res.rows:
            return [row[0] for row in res.rows]
        return []

    # ==========================================
    # 1. User Domain (Users, Addresses)
    # ==========================================
    
    def seed_users(self, count=100):
        print(f"[*] Seeding Users ({count})...")
        for _ in range(count):
            username = self.fake.unique.user_name()
            email = self.fake.unique.email()
            password_hash = self.fake.sha256()
            role_id = 2  # Customer
            
            sql = f"""
                INSERT INTO users (username, email, password_hash, role_id)
                VALUES ('{username}', '{email}', '{password_hash}', {role_id});
            """
            self._execute(sql)

    def seed_user_addresses(self):
        print("[*] Seeding User Addresses...")
        user_ids = self._get_ids("users", "user_id")
        for uid in user_ids:
            # Generate 1-3 addresses per user
            for _ in range(random.randint(1, 3)):
                city = self.fake.city().replace("'", "")
                sql = f"""
                    INSERT INTO user_addresses (user_id, address_line1, city, postal_code, country, is_default)
                    VALUES ({uid}, '{self.fake.street_address()}', '{city}', '{self.fake.zipcode()}', '{self.fake.country()}', {random.randint(0, 1)});
                """
                self._execute(sql)

    # ==========================================
    # 2. Catalog Domain (Categories, Brands, Products, Attributes, Images, Inventory)
    # ==========================================

    def seed_categories_and_brands(self):
        print("[*] Seeding Extra Categories & Brands...")
        # Add more variety beyond the initial schema seeds
        cats = [('Books', 'books'), ('Home & Garden', 'home-garden'), ('Sports', 'sports'), ('Toys', 'toys')]
        for name, slug in cats:
            self._execute(f"INSERT OR IGNORE INTO categories (name, slug) VALUES ('{name}', '{slug}')")
        
        brands = ['Nike', 'Adidas', 'Penguin', 'IKEA', 'Lego', 'Hasbro']
        for name in brands:
            self._execute(f"INSERT INTO brands (name) VALUES ('{name}')")

    def seed_products(self, count=100):
        print(f"[*] Seeding Products ({count})...")
        cat_ids = self._get_ids("categories", "category_id")
        brand_ids = self._get_ids("brands", "brand_id")
        
        adjectives = ["Ergonomic", "Rustic", "Intelligent", "Small", "Fantastic", "Practical", "Sleek"]
        materials = ["Steel", "Wooden", "Concrete", "Plastic", "Cotton", "Granite", "Rubber"]
        types_ = ["Chair", "Car", "Computer", "Keyboard", "Mouse", "Bike", "Ball", "Gloves", "Pants", "Shirt"]

        for _ in range(count):
            title = f"{random.choice(adjectives)} {random.choice(materials)} {random.choice(types_)}"
            desc = self.fake.sentence().replace("'", "")
            price = round(random.uniform(10.0, 999.0), 2)
            sku = self.fake.unique.bothify(text='??-####-???').upper()
            
            sql = f"""
                INSERT INTO products (category_id, brand_id, title, description, price, sku)
                VALUES ({random.choice(cat_ids)}, {random.choice(brand_ids)}, '{title}', '{desc}', {price}, '{sku}');
            """
            self._execute(sql)

    def seed_product_details(self):
        print("[*] Seeding Product Details (Attributes, Images, Inventory)...")
        product_ids = self._get_ids("products", "product_id")
        
        for pid in product_ids:
            # Attributes
            colors = ['Red', 'Blue', 'Black', 'White', 'Silver']
            sizes = ['S', 'M', 'L', 'XL']
            self._execute(f"INSERT INTO product_attributes (product_id, attribute_name, attribute_value) VALUES ({pid}, 'Color', '{random.choice(colors)}')")
            if random.random() > 0.5:
                self._execute(f"INSERT INTO product_attributes (product_id, attribute_name, attribute_value) VALUES ({pid}, 'Size', '{random.choice(sizes)}')")
            
            # Images
            self._execute(f"INSERT INTO product_images (product_id, image_url, is_primary) VALUES ({pid}, 'https://example.com/p/{pid}/main.jpg', 1)")
            
            # Inventory
            qty = random.randint(0, 200)
            self._execute(f"INSERT INTO inventory (product_id, quantity_in_stock) VALUES ({pid}, {qty})")

    # ==========================================
    # 3. Logistics Domain (Carriers)
    # ==========================================
    
    def seed_logistics(self):
        print("[*] Seeding Logistics (Carriers)...")
        carriers = ['DHL', 'FedEx', 'UPS', 'USPS', 'Kerry Express']
        for c in carriers:
            self._execute(f"INSERT INTO carriers (name) VALUES ('{c}')")

    # ==========================================
    # 4. Sales Domain (Coupons, Orders, Items, Invoices, Payments, Shipments)
    # ==========================================

    def seed_coupons(self):
        print("[*] Seeding Coupons...")
        for _ in range(10):
            code = self.fake.unique.bothify(text='????-##').upper()
            self._execute(f"INSERT INTO coupons (code, discount_percent) VALUES ('{code}', {random.randint(5, 50)})")

    def seed_orders(self, count=500):
        print(f"[*] Seeding Orders ({count}) & Related Data...")
        user_ids = self._get_ids("users", "user_id")
        product_ids = self._get_ids("products", "product_id") # We need prices too, simplistic here
        carrier_ids = self._get_ids("carriers", "carrier_id")
        
        # Cache product prices for performance
        prod_prices = {}
        res = self.db_repo.execute_query("SELECT product_id, price FROM products")
        if res.rows:
            prod_prices = {r[0]: r[1] for r in res.rows}

        statuses = ['pending', 'paid', 'shipped', 'delivered', 'cancelled']
        
        for _ in range(count):
            user_id = random.choice(user_ids)
            status = random.choice(statuses)
            
            # Create Order
            self._execute(f"INSERT INTO orders (user_id, total_amount, status) VALUES ({user_id}, 0, '{status}')")
            
            # Get Order ID
            # In production we'd use RETURNING id, but for sqlite compatibility sticking to max
            oid_res = self.db_repo.execute_query("SELECT MAX(order_id) FROM orders")
            order_id = oid_res.rows[0][0]

            # Add Order Items
            total_amount = 0
            for _ in range(random.randint(1, 5)):
                pid = random.choice(product_ids)
                qty = random.randint(1, 3)
                price = prod_prices.get(pid, 100)
                total_amount += price * qty
                self._execute(f"INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES ({order_id}, {pid}, {qty}, {price})")

            # Update Total
            self._execute(f"UPDATE orders SET total_amount = {total_amount} WHERE order_id = {order_id}")

            # Order Status History
            self._execute(f"INSERT INTO order_status_history (order_id, status, notes) VALUES ({order_id}, 'pending', 'Order placed')")
            if status in ['paid', 'shipped', 'delivered']:
                self._execute(f"INSERT INTO order_status_history (order_id, status) VALUES ({order_id}, 'paid')")
                # Payment
                self._execute(f"INSERT INTO payments (order_id, payment_method, amount, status) VALUES ({order_id}, 'Credit Card', {total_amount}, 'success')")
                # Invoice
                self._execute(f"INSERT INTO invoices (order_id, pdf_url) VALUES ({order_id}, 'https://store.com/invoice/{order_id}.pdf')")
            
            if status in ['shipped', 'delivered']:
                 self._execute(f"INSERT INTO order_status_history (order_id, status) VALUES ({order_id}, 'shipped')")
                 # Shipment
                 carrier = random.choice(carrier_ids) if carrier_ids else 1
                 track_no = self.fake.bothify(text='??#########??').upper()
                 self._execute(f"INSERT INTO shipments (order_id, carrier_id, tracking_number, shipped_date) VALUES ({order_id}, {carrier}, '{track_no}', CURRENT_TIMESTAMP)")

            if status == 'delivered':
                 self._execute(f"INSERT INTO order_status_history (order_id, status) VALUES ({order_id}, 'delivered')")

    # ==========================================
    # 5. Engagement Domain (Wishlists, Reviews)
    # ==========================================

    def seed_wishlists(self):
        print("[*] Seeding Wishlists...")
        user_ids = self._get_ids("users", "user_id")
        product_ids = self._get_ids("products", "product_id")

        for uid in user_ids:
            if random.random() > 0.3:
                self._execute(f"INSERT INTO wishlists (user_id, name) VALUES ({uid}, 'My Favorites')")
                # Get Wishlist ID
                res = self.db_repo.execute_query("SELECT MAX(wishlist_id) FROM wishlists")
                wid = res.rows[0][0]
                
                # Add items
                for _ in range(random.randint(1, 5)):
                    self._execute(f"INSERT INTO wishlist_items (wishlist_id, product_id) VALUES ({wid}, {random.choice(product_ids)})")

    def seed_reviews(self):
        print("[*] Seeding Reviews...")
        # Only review delivered items
        res = self.db_repo.execute_query("""
            SELECT o.user_id, oi.product_id 
            FROM orders o 
            JOIN order_items oi ON o.order_id = oi.order_id 
            WHERE o.status = 'delivered'
        """)
        if not res.success or not res.rows:
            return

        for row in res.rows:
            user_id, product_id = row
            if random.random() < 0.4: # 40% chance to review
                rating = random.randint(3, 5) # Skew positive
                comment = self.fake.sentence().replace("'", "")
                self._execute(f"INSERT INTO reviews (user_id, product_id, rating, comment) VALUES ({user_id}, {product_id}, {rating}, '{comment}')")

    # ==========================================
    # Master Seeder
    # ==========================================

    def seed_all(self, num_users=100, num_products=100, num_orders=500):
        print("\n=== INITIALIZING FULL DATABASE SEEDING ===")
        
        # 1. Independent / Static
        self.seed_categories_and_brands()
        self.seed_logistics()
        self.seed_coupons()
        
        # 2. Users
        self.seed_users(num_users)
        self.seed_user_addresses()
        
        # 3. Catalog
        self.seed_products(num_products)
        self.seed_product_details()
        
        # 4. Sales & Orders (The heavy lifting)
        self.seed_orders(num_orders)
        
        # 5. Engagement
        self.seed_wishlists()
        self.seed_reviews()
        
        print("=== SEEDING COMPLETE ===")
