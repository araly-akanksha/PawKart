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

products_data = [
    # Dog Food
    {"product_name": "Royal Canin Maxi Adult 4kg", "category": "Dog Food", "price": 2450, "sku": "RC-MAXI-4K"},
    {"product_name": "Pedigree Adult Chicken & Veg 3kg", "category": "Dog Food", "price": 780, "sku": "PD-CHK-3K"},
    {"product_name": "Drools Focus Puppy 1.2kg", "category": "Dog Food", "price": 420, "sku": "DR-PUP-12"},
    {"product_name": "Farmina N&D Grain Free 2.5kg", "category": "Dog Food", "price": 3200, "sku": "FM-GF-25"},
    {"product_name": "Hills Science Diet Adult 3kg", "category": "Dog Food", "price": 2890, "sku": "HL-SCI-3K"},
    # Cat Food
    {"product_name": "Whiskas Adult Tuna 1.2kg", "category": "Cat Food", "price": 520, "sku": "WK-TNA-12"},
    {"product_name": "Royal Canin Indoor Cat 2kg", "category": "Cat Food", "price": 1850, "sku": "RC-IND-2K"},
    {"product_name": "Sheba Melty Treats 48g", "category": "Cat Food", "price": 120, "sku": "SH-MLT-48"},
    {"product_name": "Me-O Kitten Ocean Fish 1.1kg", "category": "Cat Food", "price": 340, "sku": "MO-KIT-11"},
    # Dog Treats
    {"product_name": "Pedigree Dentastix Medium 7pc", "category": "Dog Treats", "price": 250, "sku": "PD-DNT-7M"},
    {"product_name": "Drools Chicken Jerky 100g", "category": "Dog Treats", "price": 180, "sku": "DR-JRK-1H"},
    {"product_name": "Gnawlers Bones Large", "category": "Dog Treats", "price": 150, "sku": "GN-BNE-LG"},
    # Accessories
    {"product_name": "Adjustable Dog Collar (M)", "category": "Accessories", "price": 350, "sku": "AC-CLR-MD"},
    {"product_name": "Retractable Leash 5m", "category": "Accessories", "price": 650, "sku": "AC-LSH-5M"},
    {"product_name": "Stainless Steel Bowl Set", "category": "Accessories", "price": 480, "sku": "AC-BWL-SS"},
    {"product_name": "Pet Carrier Bag (Small)", "category": "Accessories", "price": 1200, "sku": "AC-CRR-SM"},
    # Grooming
    {"product_name": "Flea & Tick Shampoo 200ml", "category": "Grooming", "price": 320, "sku": "GR-FTS-2H"},
    {"product_name": "Slicker Brush (Medium)", "category": "Grooming", "price": 280, "sku": "GR-BRS-MD"},
    {"product_name": "Nail Clipper Professional", "category": "Grooming", "price": 220, "sku": "GR-NLC-PR"},
    # Health
    {"product_name": "Himalaya Healthy Pet Multivitamin", "category": "Health", "price": 390, "sku": "HL-MUL-HM"},
    {"product_name": "Frontline Plus Spot-On (M)", "category": "Health", "price": 560, "sku": "HL-FLP-MD"},
    {"product_name": "Drools Joint Support 50 tabs", "category": "Health", "price": 450, "sku": "HL-JNT-50"},
    # Bird Food
    {"product_name": "Vitapol Budgie Mix 500g", "category": "Bird Food", "price": 180, "sku": "BF-BDG-5H"},
    {"product_name": "Zupreem Parrot Pellets 1kg", "category": "Bird Food", "price": 850, "sku": "BF-PRT-1K"},
    # Fish
    {"product_name": "Optimum Goldfish Pellets 100g", "category": "Fish Food", "price": 140, "sku": "FF-GLD-1H"},
]

products = []
for pd in products_data:
    p = Product(
        product_name=pd["product_name"],
        category=pd["category"],
        price=pd["price"],
        sku=pd["sku"],
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
