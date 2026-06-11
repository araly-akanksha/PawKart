"""
Import Flipkart Scraped Pet Products into PawKart Database
===========================================================
Reads flipkart_pet_products.csv (400 products scraped via Selenium)
and imports them into the PawKart PostgreSQL database.

- Cleans prices (removes ₹ symbol and commas)
- Extracts categories from product names
- Generates unique SKUs
- Creates inventory entries with randomized stock
- Creates sample orders from imported products
- Creates RFID events for realistic dashboard data

Run:  cd backend && python import_flipkart.py
"""

import sys
import os
import re
import random
import hashlib
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(__file__))

import pandas as pd
from app.database import SessionLocal, engine
from app.models import Base, Product, Inventory, Order, OrderItem, Store

# ── Configuration ────────────────────────────────────────────
CSV_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Datasets', 'flipkart_pet_products.csv')

# ── Category detection from product names ────────────────────
CATEGORY_KEYWORDS = {
    "Dog Food": ["dog food", "dog treat", "dog chew", "dog biscuit", "puppy food", "pedigree", "drools",
                 "royal canin", "dog nutrition", "dog meal"],
    "Cat Food": ["cat food", "cat treat", "kitten food", "whiskas", "me-o", "sheba",
                 "cat nutrition", "cat meal", "cat biscuit"],
    "Dog Grooming": ["dog shampoo", "dog conditioner", "dog brush", "dog comb", "flea", "tick",
                     "anti-fungal", "anti-microbial", "pet shampoo", "pet wash", "grooming",
                     "coat cleanser", "pet care"],
    "Dog Accessories": ["dog collar", "dog leash", "dog harness", "dog bed", "dog bowl",
                        "dog toy", "chew toy", "squeaky", "rope toy", "ball toy", "frisbee"],
    "Cat Accessories": ["cat collar", "cat toy", "cat bed", "cat bowl", "scratching",
                        "litter", "cat tree", "cat tunnel"],
    "Pet Health": ["vitamin", "supplement", "medicine", "dewormer", "spot-on",
                   "health", "multivitamin", "joint", "digestive", "probiotic"],
    "Bird Food": ["bird food", "bird seed", "budgie", "parrot", "cockatiel", "bird treat"],
    "Fish Food": ["fish food", "fish pellet", "goldfish", "aquarium", "fish flake"],
    "Pet Clothing": ["pet cloth", "dog cloth", "cat cloth", "pet dress", "dog jacket",
                     "raincoat", "sweater", "costume"],
    "Pet Carrier": ["carrier", "cage", "crate", "kennel", "travel bag", "pet bag"],
}


def detect_category(product_name):
    """Detect product category from the product name."""
    name_lower = product_name.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in name_lower:
                return category

    # Fallback heuristics
    if any(w in name_lower for w in ["dog", "puppy", "canine"]):
        return "Dog Accessories"
    if any(w in name_lower for w in ["cat", "kitten", "feline"]):
        return "Cat Accessories"
    if any(w in name_lower for w in ["bird", "parrot", "budgie"]):
        return "Bird Food"
    if any(w in name_lower for w in ["fish", "aqua"]):
        return "Fish Food"

    return "Pet Supplies"


def clean_price(price_str):
    """Clean price string: remove ₹, commas, spaces; return float."""
    if pd.isna(price_str) or not str(price_str).strip():
        return 0.0
    cleaned = re.sub(r'[₹,\s]', '', str(price_str))
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def generate_sku(product_name, index):
    """Generate a unique SKU from product name."""
    hash_part = hashlib.md5(product_name.encode()).hexdigest()[:4].upper()
    return f"FK-{index:04d}-{hash_part}"


def clean_rating(rating_str):
    """Extract numeric rating from string like '4.4'."""
    if pd.isna(rating_str) or not str(rating_str).strip():
        return None
    try:
        return float(str(rating_str).strip())
    except ValueError:
        return None


def clean_reviews(review_str):
    """Extract review count from string like '(1,543)'."""
    if pd.isna(review_str) or not str(review_str).strip():
        return 0
    cleaned = re.sub(r'[(),\s]', '', str(review_str))
    try:
        return int(cleaned)
    except ValueError:
        return 0


# ── Main Import Logic ────────────────────────────────────────

def main():
    print("=" * 60)
    print("  FLIPKART PET PRODUCTS IMPORTER")
    print("  Importing your web-scraped data into PawKart")
    print("=" * 60)
    print()

    # Read CSV
    print(f"Reading CSV: {CSV_PATH}")
    df = pd.read_csv(CSV_PATH, encoding='utf-8-sig')
    print(f"  Found {len(df)} products with columns: {list(df.columns)}")
    print()

    # Remove duplicates by product name
    original_count = len(df)
    df = df.drop_duplicates(subset=['Product Name'], keep='first')
    df = df[df['Product Name'].str.strip().str.len() > 0]  # remove empty names
    print(f"  After deduplication: {len(df)} products (removed {original_count - len(df)} duplicates)")

    # Create DB session
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Clear existing data
    print()
    print("Clearing existing data...")
    db.query(OrderItem).delete()
    db.query(Order).delete()
    db.query(Inventory).delete()
    db.query(Product).delete()
    db.query(Store).delete()
    db.commit()

    # ── Import Products ──────────────────────────────────────
    print()
    print("Importing products...")
    products = []
    categories_count = {}

    for idx, row in df.iterrows():
        name = str(row['Product Name']).strip()
        if not name:
            continue

        price = clean_price(row['Price'])
        if price <= 0:
            price = random.uniform(100, 2000)  # assign random price if missing

        category = detect_category(name)
        sku = generate_sku(name, len(products) + 1)
        image_url = str(row.get('Image URL', '')).strip()
        if image_url == 'nan' or not image_url:
            image_url = None

        product = Product(
            product_name=name[:200],  # truncate long names
            description=f"Flipkart Pet Product | Rating: {row.get('Rating', 'N/A')} | Reviews: {row.get('Reviews', 'N/A')} | Discount: {row.get('Discount', 'N/A')}",
            category=category,
            price=round(price, 2),
            sku=sku,
            image_url=image_url,
            available=True,
        )
        db.add(product)
        products.append(product)

        categories_count[category] = categories_count.get(category, 0) + 1

    db.flush()  # assign IDs
    print(f"  Imported {len(products)} products across {len(categories_count)} categories:")
    for cat, count in sorted(categories_count.items(), key=lambda x: -x[1]):
        print(f"    {cat}: {count}")

    # ── Create Inventory ─────────────────────────────────────
    print()
    print("Creating inventory records...")
    low_stock_count = 0

    for product in products:
        stock = random.randint(0, 150)
        reorder = random.randint(10, 40)
        health = min(100.0, max(0.0, (stock / max(reorder, 1)) * 50))

        inv = Inventory(
            product_id=product.id,
            current_stock=stock,
            reorder_level=reorder,
            unit="pcs",
            inventory_health_score=round(health, 1),
        )
        db.add(inv)
        if stock <= reorder:
            low_stock_count += 1

    db.flush()
    print(f"  Created {len(products)} inventory records ({low_stock_count} low-stock alerts)")

    # (RFID Events removed in Phase 1)

    # ── Create Orders ────────────────────────────────────────
    print()
    print("Creating sample orders...")

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
        ("Ananya Das", "+91-9123456780", "22 Park Street, Kolkata"),
        ("Karthik Rajan", "+91-8234567890", "88 T Nagar, Chennai"),
        ("Pooja Verma", "+91-7345678901", "55 Sector 18, Noida"),
        ("Nitin Agarwal", "+91-6456789012", "31 Aundh, Pune"),
        ("Divya Krishnan", "+91-5567890123", "76 HSR Layout, Bengaluru"),
    ]

    delivery_slots = ["09:00-10:00", "10:00-11:00", "11:00-12:00",
                      "14:00-15:00", "16:00-17:00", "18:00-19:00"]
    statuses = ["pending", "confirmed", "preparing", "out_for_delivery",
                "delivered", "delivered", "delivered", "cancelled"]

    order_count = 0
    total_items = 0

    for i in range(75):  # 75 orders for a realistic dashboard
        cust = random.choice(customers)
        num_items = random.randint(1, 5)
        order_products = random.sample(products, min(num_items, len(products)))
        total = 0

        days_ago = random.randint(0, 29)
        created = datetime.utcnow() - timedelta(
            days=days_ago,
            hours=random.randint(8, 20),
            minutes=random.randint(0, 59),
        )

        status = random.choice(statuses)
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
                subtotal=round(subtotal, 2),
            ))
            total_items += 1

        order = Order(
            customer_name=cust[0],
            customer_phone=cust[1],
            customer_address=cust[2],
            delivery_slot=random.choice(delivery_slots),
            total_amount=round(total, 2),
            status=status,
            created_at=created,
            updated_at=created + timedelta(minutes=random.randint(5, 120)) if status != "pending" else created,
            items=items,
        )
        db.add(order)
        order_count += 1

    print(f"  Created {order_count} orders with {total_items} items")

    # ── Create Store Profile ─────────────────────────────────
    print()
    print("Creating store profile...")
    store = Store(
        name="PawKart Pet Store",
        owner_name="Araly Akanksha",
        email="store@pawkart.in",
        phone="+91-9876543210",
        address="45 Pet Street, Bengaluru, Karnataka 560001",
        is_open=True,
        opening_time="09:00",
        closing_time="21:00",
        delivery_radius_km=8.0,
        min_order_amount=200.0,
    )
    db.add(store)

    # ── Commit ───────────────────────────────────────────────
    db.commit()
    db.close()

    print()
    print("=" * 60)
    print("  IMPORT COMPLETE!")
    print("=" * 60)
    print(f"  Products:      {len(products)} (from Flipkart web scraping)")
    print(f"  Categories:    {len(categories_count)}")
    print(f"  Inventory:     {len(products)} records ({low_stock_count} low-stock)")
    print(f"  Orders:        {order_count} ({total_items} items)")
    print(f"  Store:         1 profile")
    print()
    print("  Data Source:   Flipkart Web Scraping (Selenium)")
    print("  CSV File:      flipkart_pet_products.csv")
    print("  Records:       400 scraped products")
    print()
    print("  Open http://localhost:5174 to see the dashboard!")
    print("=" * 60)


if __name__ == "__main__":
    main()
