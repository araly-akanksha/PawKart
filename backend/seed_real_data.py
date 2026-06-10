"""
PawKart Seed Data Script
========================
Populates the database with realistic pet store products,
inventory, and orders for 5 independent stores.

Run: cd backend && python seed_data.py
"""
import sys
import os
import random
from datetime import datetime, timedelta

# Add parent to path for app imports
sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal, engine
from app.models import Base, Product, Inventory, Order, OrderItem, Store

# ── Create tables ────────────────────────────────────────────
Base.metadata.drop_all(bind=engine) # Drop to apply new constraints safely
Base.metadata.create_all(bind=engine)
db = SessionLocal()

# ── Store ────────────────────────────────────────────────────
print("Creating 5 store profiles...")

store_names = ["Koramangala Branch", "Indiranagar Branch", "Whitefield Branch", "Jayanagar Branch", "HSR Layout Branch"]
stores = []
for name in store_names:
    s = Store(
        name=name,
        owner_name="Yeshwanth",
        email=f"{name.split()[0].lower()}@pawkart.in",
        phone="+91-9876543210",
        address=f"Main Road, {name.split()[0]}, Bengaluru",
        is_open=True,
        opening_time="09:00",
        closing_time="21:00",
        delivery_radius_km=8.0,
        min_order_amount=200.0,
    )
    db.add(s)
    stores.append(s)

db.flush()

# ── Products ─────────────────────────────────────────────────
print("Creating products...")


import pandas as pd
import re as regex_lib
import hashlib

def clean_price(price_str):
    if pd.isna(price_str) or not str(price_str).strip(): return 0.0
    cleaned = regex_lib.sub(r'[₹,\s]', '', str(price_str))
    try: return float(cleaned)
    except ValueError: return 0.0

def generate_sku(name, idx):
    return f"FK-{idx:04d}-{hashlib.md5(name.encode()).hexdigest()[:4].upper()}"

CATEGORY_KEYWORDS = {
    "Dog Food": ["dog food", "dog treat", "dog chew", "dog biscuit", "puppy food", "pedigree", "drools", "royal canin"],
    "Cat Food": ["cat food", "cat treat", "kitten food", "whiskas", "me-o", "sheba"],
    "Grooming": ["dog shampoo", "dog conditioner", "dog brush", "dog comb", "flea", "tick", "grooming", "shampoo"],
    "Accessories": ["dog collar", "dog leash", "dog harness", "dog bed", "dog bowl", "dog toy", "cat collar", "cat toy", "carrier"],
    "Health": ["vitamin", "supplement", "medicine", "dewormer", "spot-on", "health", "multivitamin"],
    "Bird Food": ["bird food", "bird seed", "budgie", "parrot"],
    "Fish Food": ["fish food", "fish pellet", "goldfish", "aquarium"],
}

def detect_category(product_name):
    name_lower = product_name.lower()
    for cat, keywords in CATEGORY_KEYWORDS.items():
        if any(k in name_lower for k in keywords): return cat
    if "dog" in name_lower: return "Dog Food"
    if "cat" in name_lower: return "Cat Food"
    if "bird" in name_lower: return "Bird Food"
    if "fish" in name_lower or "aqua" in name_lower: return "Fish Food"
    return "Accessories"

df = pd.read_csv(r'C:\Users\yeshw\Documents\GitHub\PawKart\Datasets\flipkart_pet_products.csv', encoding='utf-8-sig')
df = df.drop_duplicates(subset=['Product Name'], keep='first')
df = df[df['Product Name'].str.strip().str.len() > 0]

products = []
for idx, row in df.iterrows():
    name = str(row['Product Name']).strip()
    price = clean_price(row['Price'])
    if price <= 0: price = random.uniform(100, 2000)
    
    category = detect_category(name)
    sku = generate_sku(name, len(products) + 1)
    
    image_url = str(row.get('Image URL', '')).strip()
    if image_url == 'nan' or not image_url: image_url = None
    
    p = Product(
        product_name=name[:200],
        category=category,
        price=round(price, 2),
        sku=sku,
        image_url=image_url,
        available=True,
    )
    db.add(p)
    products.append(p)

db.flush()

# ── Inventory ────────────────────────────────────────────────
print("Creating inventory across 5 stores...")

inventory_count = 0
for store in stores:
    for p in products:
        stock = random.randint(5, 120)
        reorder = random.randint(10, 30)
        inv = Inventory(
            product_id=p.id,
            store_id=store.id,
            current_stock=stock,
            reorder_level=reorder,
            unit="pcs",
        )
        db.add(inv)
        inventory_count += 1

db.flush()
print(f"  Created {inventory_count} inventory records")

# ── Orders ───────────────────────────────────────────────────
print("Creating historical orders for forecasting...")

customers = [
    ("Rahul Sharma", "+91-9876543210", "42 MG Road, Bengaluru"),
    ("Priya Patel", "+91-9988776655", "15 Anna Nagar, Chennai"),
    ("Arjun Mehta", "+91-8765432109", "78 SG Highway, Ahmedabad"),
    ("Sneha Reddy", "+91-7654321098", "23 Jubilee Hills, Hyderabad"),
    ("Vikram Singh", "+91-6543210987", "91 Connaught Place, New Delhi"),
    ("Kavya Nair", "+91-9012345678", "56 Marine Drive, Kochi"),
    ("Rohit Kumar", "+91-8901234567", "33 Salt Lake, Kolkata"),
    ("Meera Joshi", "+91-7890123456", "12 Koregaon Park, Pune"),
    ("Amit Gupta", "+91-6789012345", "67 Vaishali Nagar, Jaipur"),
    ("Deepa Iyer", "+91-5678901234", "44 Indira Nagar, Bengaluru"),
]

delivery_slots = ["09:00-10:00", "10:00-11:00", "11:00-12:00", "14:00-15:00", "16:00-17:00", "18:00-19:00"]
statuses = ["pending", "confirmed", "preparing", "out_for_delivery", "delivered", "delivered", "delivered", "cancelled"]

order_count = 0
# Generate 12 months of synthetic history across all stores
for i in range(250):
    cust = random.choice(customers)
    store = random.choice(stores)
    num_items = random.randint(1, 4)
    order_products = random.sample(products, min(num_items, len(products)))
    total = 0

    days_ago = random.randint(0, 360)
    created = datetime.utcnow() - timedelta(
        days=days_ago,
        hours=random.randint(8, 20),
        minutes=random.randint(0, 59),
    )

    status = "delivered"
    if days_ago <= 1:
        status = random.choice(["pending", "confirmed", "preparing"])

    items = []
    for op in order_products:
        qty = random.randint(1, 3)
        subtotal = op.price * qty
        total += subtotal
        items.append(OrderItem(
            product_id=op.id,
            product_name=op.product_name,
            quantity=qty,
            unit_price=op.price,
            subtotal=subtotal,
        ))

    order = Order(
        customer_name=cust[0],
        customer_phone=cust[1],
        customer_address=cust[2],
        delivery_slot=random.choice(delivery_slots),
        total_amount=round(total, 2),
        status=status,
        store_id=store.id,
        created_at=created,
        updated_at=created + timedelta(minutes=random.randint(5, 120)) if status != "pending" else created,
        items=items,
    )
    db.add(order)
    order_count += 1

print(f"  Created {order_count} historical orders")

# ── Commit everything ────────────────────────────────────────
db.commit()
db.close()

print()
print("=" * 50)
print("SEED DATA COMPLETE!")
print("=" * 50)
print(f"  Products:     {len(products)}")
print(f"  Stores:       {len(stores)}")
print(f"  Inventory:    {inventory_count} records")
print(f"  Orders:       {order_count}")
print("=" * 50)
