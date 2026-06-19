import sqlite3
from datetime import datetime, timedelta

conn = sqlite3.connect('crm.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS orders (customer_name TEXT, order_id TEXT PRIMARY KEY, category TEXT, status TEXT, purchase_date TEXT, price REAL)''')

now = datetime.now()
valid = (now - timedelta(days=12)).strftime('%Y-%m-%d')
expired = (now - timedelta(days=40)).strftime('%Y-%m-%d')

data = [
    ("Aarav Patel", "ORD-101", "Clothing", "delivered", valid, 45.00),
    ("Priya Sharma", "ORD-102", "Electronics", "delivered", valid, 800.00),
    ("Rahul Singh", "ORD-103", "Digital Goods", "delivered", valid, 60.00),
    ("Neha Gupta", "ORD-104", "Clothing", "delivered", expired, 55.00),
    ("Amit Kumar", "ORD-105", "Electronics", "damaged_in_transit", expired, 1200.00)
]

c.executemany('INSERT OR IGNORE INTO orders VALUES (?, ?, ?, ?, ?, ?)', data)
conn.commit()
conn.close()
print("Database crm.db created!")