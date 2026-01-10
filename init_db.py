import sqlite3
import os

DB_PATH = "data/sqlite.db"

# Ensure data directory exists
os.makedirs("data", exist_ok=True)

if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

try:
    conn = sqlite3.connect(DB_PATH)
    with open("schema.sql", "r") as f:
        schema = f.read()
    conn.executescript(schema)
    conn.commit()
    conn.close()
    print(f"Database initialized successfully at {DB_PATH}.")
except Exception as e:
    print(f"Error initializing database: {e}")
