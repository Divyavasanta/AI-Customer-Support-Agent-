import sqlite3
from datetime import datetime, timedelta
import random

def create_mock_database():
    conn = sqlite3.connect('crm.db')
    cursor = conn.cursor()

    # Table banate hain
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            order_id TEXT PRIMARY KEY,
            customer_name TEXT,
            product_category TEXT,
            purchase_date TEXT,
            status TEXT,
            price REAL
        )
    ''')

    # Purana data clear karne ke liye (agar run karte waqt duplicate error aaye)
    cursor.execute('DELETE FROM orders')

    # Aaj ki date se calculate karne ke liye
    today = datetime.now()
    
    # 25 Diverse Mock Profiles
    mock_orders = [
        # --- Standard Valid Refunds (Under 30 days) ---
        ('ORD-101', 'Aarav Sharma', 'Electronics', (today - timedelta(days=10)).strftime('%Y-%m-%d'), 'Delivered', 1200.00),
        ('ORD-102', 'Isha Patel', 'Clothing', (today - timedelta(days=5)).strftime('%Y-%m-%d'), 'Delivered', 450.00),
        ('ORD-103', 'Rohan Singh', 'Home & Kitchen', (today - timedelta(days=20)).strftime('%Y-%m-%d'), 'Delivered', 899.99),
        ('ORD-104', 'Priya Gupta', 'Toys', (today - timedelta(days=15)).strftime('%Y-%m-%d'), 'Delivered', 299.50),
        ('ORD-105', 'Kabir Das', 'Clothing', (today - timedelta(days=2)).strftime('%Y-%m-%d'), 'Delivered', 750.00),
        
        # --- Edge Cases: Past 30 Days (Policy Denial) ---
        ('ORD-201', 'Ananya Verma', 'Electronics', (today - timedelta(days=45)).strftime('%Y-%m-%d'), 'Delivered', 2500.00),
        ('ORD-202', 'Vikram Malhotra', 'Clothing', (today - timedelta(days=35)).strftime('%Y-%m-%d'), 'Delivered', 600.00),
        ('ORD-203', 'Neha Reddy', 'Home & Kitchen', (today - timedelta(days=60)).strftime('%Y-%m-%d'), 'Delivered', 150.00),
        ('ORD-204', 'Arjun Kapoor', 'Toys', (today - timedelta(days=100)).strftime('%Y-%m-%d'), 'Delivered', 45.00),
        
        # --- Edge Cases: Non-Refundable Items (e.g., Software/Digital) ---
        ('ORD-301', 'Sanya Iyer', 'Software', (today - timedelta(days=5)).strftime('%Y-%m-%d'), 'Delivered', 99.99),
        ('ORD-302', 'Rahul Joshi', 'Digital Gift Card', (today - timedelta(days=10)).strftime('%Y-%m-%d'), 'Delivered', 50.00),
        ('ORD-303', 'Meera Rajput', 'Software', (today - timedelta(days=2)).strftime('%Y-%m-%d'), 'Delivered', 199.00),
        
        # --- Edge Cases: Order Not Delivered Yet (In Transit / Processing) ---
        ('ORD-401', 'Karan Mehta', 'Electronics', (today - timedelta(days=2)).strftime('%Y-%m-%d'), 'Shipped', 3400.00),
        ('ORD-402', 'Pooja Nair', 'Clothing', (today - timedelta(days=1)).strftime('%Y-%m-%d'), 'Processing', 890.00),
        ('ORD-403', 'Aditya Sen', 'Home & Kitchen', today.strftime('%Y-%m-%d'), 'Processing', 210.00),
        
        # --- Random Mix for extra testing ---
        ('ORD-501', 'Simran Kaur', 'Clothing', (today - timedelta(days=12)).strftime('%Y-%m-%d'), 'Delivered', 1120.00),
        ('ORD-502', 'Manish Tiwari', 'Electronics', (today - timedelta(days=28)).strftime('%Y-%m-%d'), 'Delivered', 4500.00),
        ('ORD-503', 'Shruti Hassan', 'Software', (today - timedelta(days=40)).strftime('%Y-%m-%d'), 'Delivered', 299.00),
        ('ORD-504', 'Deepak Chahar', 'Toys', (today - timedelta(days=18)).strftime('%Y-%m-%d'), 'Delivered', 340.00),
        ('ORD-505', 'Anjali Menon', 'Home & Kitchen', (today - timedelta(days=32)).strftime('%Y-%m-%d'), 'Delivered', 760.00),
        ('ORD-506', 'Ravi Teja', 'Electronics', (today - timedelta(days=31)).strftime('%Y-%m-%d'), 'Delivered', 800.00),
        ('ORD-507', 'Kavita Roy', 'Clothing', (today - timedelta(days=8)).strftime('%Y-%m-%d'), 'Shipped', 150.00),
        ('ORD-508', 'Tariq Khan', 'Digital Gift Card', (today - timedelta(days=1)).strftime('%Y-%m-%d'), 'Delivered', 100.00),
        ('ORD-509', 'Sneha Paul', 'Home & Kitchen', (today - timedelta(days=22)).strftime('%Y-%m-%d'), 'Delivered', 540.00),
        ('ORD-510', 'Yash Chopra', 'Electronics', (today - timedelta(days=3)).strftime('%Y-%m-%d'), 'Delivered', 12500.00),
    ]

    cursor.executemany('''
        INSERT INTO orders (order_id, customer_name, product_category, purchase_date, status, price)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', mock_orders)

    conn.commit()
    conn.close()
    print("Database successfully populated with 25 diverse records!")

if __name__ == "__main__":
    create_mock_database()