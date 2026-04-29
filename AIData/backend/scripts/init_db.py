#!/usr/bin/env python3
"""
Initialize business database with sample data.
Creates: products, orders, customers tables with realistic data.
"""
import sqlite3
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "business.db"

# Remove existing DB to start fresh
if DB_PATH.exists():
    DB_PATH.unlink()

conn = sqlite3.connect(str(DB_PATH))
c = conn.cursor()

# --- Products ---
c.execute("""
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    price REAL NOT NULL,
    stock INTEGER NOT NULL DEFAULT 0,
    created_at TEXT DEFAULT (date('now'))
);
""")

products = [
    (1, "MacBook Pro 16\"", "Electronics", 19999.00, 45),
    (2, "iPhone 15 Pro", "Electronics", 8999.00, 120),
    (3, "AirPods Pro 2", "Electronics", 1899.00, 300),
    (4, "iPad Air", "Electronics", 4999.00, 80),
    (5, "Apple Watch Ultra 2", "Electronics", 6499.00, 60),
    (6, "戴森V15吸尘器", "Home Appliances", 5499.00, 35),
    (7, "小米扫地机器人", "Home Appliances", 2999.00, 90),
    (8, "飞利浦空气炸锅", "Home Appliances", 1299.00, 150),
    (9, "SK-II神仙水", "Cosmetics", 899.00, 200),
    (10, "兰蔻小黑瓶精华", "Cosmetics", 768.00, 180),
    (11, "Nike Air Max", "Fashion", 999.00, 250),
    (12, "Adidas Ultraboost", "Fashion", 1299.00, 200),
    (13, "北面羽绒服", "Fashion", 2599.00, 100),
    (14, "施华洛世奇项链", "Fashion", 699.00, 80),
    (15, "Kindle Paperwhite", "Books & Media", 1299.00, 110),
]
c.executemany("INSERT INTO products VALUES (?, ?, ?, ?, ?, date('now'))", products)

# --- Customers ---
c.execute("""
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    city TEXT NOT NULL,
    age INTEGER NOT NULL,
    vip_level TEXT DEFAULT 'normal',
    created_at TEXT DEFAULT (date('now'))
);
""")

customers = [
    (1, "张伟", "zhangwei@example.com", "北京", 32, "gold"),
    (2, "李娜", "lina@example.com", "上海", 28, "silver"),
    (3, "王芳", "wangfang@example.com", "深圳", 35, "gold"),
    (4, "刘洋", "liuyang@example.com", "广州", 41, "normal"),
    (5, "陈明", "chenming@example.com", "杭州", 26, "silver"),
    (6, "杨丽", "yangli@example.com", "成都", 30, "normal"),
    (7, "周杰", "zhoujie@example.com", "武汉", 38, "gold"),
    (8, "吴婷", "wuting@example.com", "西安", 24, "normal"),
    (9, "赵雷", "zhaolei@example.com", "南京", 45, "gold"),
    (10, "孙静", "sunjing@example.com", "重庆", 29, "silver"),
    (11, "马超", "machao@example.com", "天津", 33, "normal"),
    (12, "胡歌", "huge@example.com", "苏州", 36, "gold"),
    (13, "林志玲", "linzhiling@example.com", "台北", 50, "vip"),
    (14, "黄晓明", "huangxiaoming@example.com", "青岛", 39, "silver"),
    (15, "徐峥", "xuzheng@example.com", "长沙", 44, "gold"),
]
c.executemany("INSERT INTO customers VALUES (?, ?, ?, ?, ?, ?, date('now'))", customers)

# --- Orders ---
c.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    total_amount REAL NOT NULL,
    status TEXT DEFAULT 'pending',
    created_at TEXT DEFAULT (date('now')),
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);
""")

import random
import datetime

random.seed(42)
statuses = ["completed", "pending", "cancelled", "shipped"]
order_id = 1
order_records = []
for month in range(1, 6):
    for _ in range(30):
        cid = random.randint(1, 15)
        pid = random.randint(1, 15)
        qty = random.randint(1, 5)
        price = [p[3] for p in products if p[0] == pid][0]
        total = round(price * qty * random.uniform(0.85, 1.0), 2)
        status = random.choices(statuses, weights=[60, 20, 10, 10])[0]
        day = random.randint(1, 28)
        date_str = f"2026-{month:02d}-{day:02d}"
        order_records.append((order_id, cid, pid, qty, total, status, date_str))
        order_id += 1

c.executemany(
    "INSERT INTO orders (id, customer_id, product_id, quantity, total_amount, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
    order_records,
)

conn.commit()

# Print summary
c.execute("SELECT COUNT(*) FROM products")
c.execute("SELECT COUNT(*) FROM customers")
c.execute("SELECT COUNT(*) FROM orders")
print(f"Database created: {DB_PATH}")
print(f"  Products: {c.execute('SELECT COUNT(*) FROM products').fetchone()[0]}")
print(f"  Customers: {c.execute('SELECT COUNT(*) FROM customers').fetchone()[0]}")
print(f"  Orders: {c.execute('SELECT COUNT(*) FROM orders').fetchone()[0]}")

conn.close()
