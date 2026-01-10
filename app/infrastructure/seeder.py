from faker import Faker
import random
from app.infrastructure.sqlite_db import SqliteRepository

class DataSeeder:
    def __init__(self, db_repo: SqliteRepository):
        self.db_repo = db_repo
        self.fake = Faker()

    def seed_users(self, count=10):
        print(f"[*] Seeding {count} users...")
        for _ in range(count):
            username = self.fake.user_name()
            email = self.fake.email()
            password_hash = self.fake.sha256()
            role_id = 2  # Customer
            
            sql = f"""
                INSERT INTO users (username, email, password_hash, role_id)
                VALUES ('{username}', '{email}', '{password_hash}', {role_id});
            """
            self.db_repo.execute_query(sql)

    def seed_products(self, count=20):
        print(f"[*] Seeding {count} products...")
        # Predefined categories (IDs 1-4 from schema.sql) and brands (IDs 1-4)
        adjectives = ["Super", "Ultra", "Pro", "Max", "Lite", "Smart", "Eco"]
        nouns = ["Widget", "Gadget", "Device", "System", "Module", "Unit"]
        
        for _ in range(count):
            category_id = random.randint(1, 4)
            brand_id = random.randint(1, 4)
            title = f"{random.choice(adjectives)} {random.choice(nouns)} {random.randint(100, 999)}"
            description = self.fake.sentence()
            price = round(random.uniform(10.0, 2000.0), 2)
            sku = self.fake.bothify(text='??-####-???').upper()
            
            sql = f"""
                INSERT INTO products (category_id, brand_id, title, description, price, sku)
                VALUES ({category_id}, {brand_id}, '{title}', '{description}', {price}, '{sku}');
            """
            self.db_repo.execute_query(sql)

    def seed_orders(self, count=50):
        print(f"[*] Seeding {count} orders...")
        # Need valid user IDs. Assuming we just seeded 10 + 3 initial = ~13 users.
        # Let's get actual IDs to be safe.
        users_res = self.db_repo.execute_query("SELECT user_id FROM users")
        if not users_res.success:
            print("[!] Failed to get users for order seeding.")
            return
        user_ids = [row[0] for row in users_res.rows]

        products_res = self.db_repo.execute_query("SELECT product_id, price FROM products")
        if not products_res.success:
            print("[!] Failed to get products for order seeding.")
            return
        products = products_res.rows # List of (id, price)

        statuses = ['pending', 'paid', 'shipped', 'delivered', 'cancelled']

        for _ in range(count):
            user_id = random.choice(user_ids)
            status = random.choice(statuses)
            
            # Create Order first
            # We don't have total_amount yet, set 0 and update later
            sql_order = f"""
                INSERT INTO orders (user_id, total_amount, status)
                VALUES ({user_id}, 0, '{status}');
            """
            self.db_repo.execute_query(sql_order)
            
            # Get last order ID (naive approach, strict would use RETURNING or fetch max)
            order_id_res = self.db_repo.execute_query("SELECT MAX(order_id) FROM orders")
            order_id = order_id_res.rows[0][0]

            # Add Order Items
            num_items = random.randint(1, 5)
            total = 0
            for _ in range(num_items):
                prod = random.choice(products) # (id, price)
                p_id = prod[0]
                price = prod[1]
                qty = random.randint(1, 3)
                total += price * qty
                
                sql_item = f"""
                    INSERT INTO order_items (order_id, product_id, quantity, unit_price)
                    VALUES ({order_id}, {p_id}, {qty}, {price});
                """
                self.db_repo.execute_query(sql_item)

            # Update Order Total
            sql_update = f"UPDATE orders SET total_amount = {total} WHERE order_id = {order_id}"
            self.db_repo.execute_query(sql_update)

    def seed_reviews(self):
        print("[*] Seeding reviews...")
        # Get Delivered Orders to make verified reviews
        orders_res = self.db_repo.execute_query("SELECT order_id, user_id FROM orders WHERE status = 'delivered'")
        if not orders_res.success: return

        for row in orders_res.rows:
            order_id, user_id = row
            # Get items from this order
            items_res = self.db_repo.execute_query(f"SELECT product_id FROM order_items WHERE order_id = {order_id}")
            if not items_res.success: continue
            
            for item in items_res.rows:
                product_id = item[0]
                # 30% chance to review
                if random.random() < 0.3:
                    rating = random.randint(1, 5)
                    comment = self.fake.sentence()
                    sql = f"""
                        INSERT INTO reviews (product_id, user_id, rating, comment)
                        VALUES ({product_id}, {user_id}, {rating}, '{comment}');
                    """
                    self.db_repo.execute_query(sql)

    def seed_all(self):
        print("--- Starting Seeding Process ---")
        self.seed_users(10)
        self.seed_products(20)
        self.seed_orders(50)
        self.seed_reviews()
        print("--- Seeding Completed ---")
