"""PawKart API End-to-End Test"""
import urllib.request
import json


def get(url):
    r = urllib.request.urlopen(url)
    return json.loads(r.read())


def post(url, data):
    req = urllib.request.Request(
        url, json.dumps(data).encode(), {"Content-Type": "application/json"}
    )
    r = urllib.request.urlopen(req)
    return json.loads(r.read())


def patch(url, data):
    req = urllib.request.Request(
        url, json.dumps(data).encode(), {"Content-Type": "application/json"}
    )
    req.method = "PATCH"
    r = urllib.request.urlopen(req)
    return json.loads(r.read())


BASE = "http://127.0.0.1:8000"

# 1. Health check
print("=== HEALTH ===")
print(get(BASE + "/"))
print(get(BASE + "/healthz"))

# 2. Create products
print("\n=== CREATE PRODUCTS ===")
p1 = post(BASE + "/products", {
    "product_name": "Royal Canin Dog Food 3kg",
    "category": "Dog Food",
    "price": 1450.0,
    "sku": "RC-DOG-3K"
})
print("Product 1:", p1["product_name"], "(id=" + str(p1["id"]) + ")")

p2 = post(BASE + "/products", {
    "product_name": "Whiskas Cat Food 1.2kg",
    "category": "Cat Food",
    "price": 520.0,
    "sku": "WK-CAT-12"
})
print("Product 2:", p2["product_name"], "(id=" + str(p2["id"]) + ")")

p3 = post(BASE + "/products", {
    "product_name": "Pedigree Dentastix",
    "category": "Dog Treats",
    "price": 250.0,
    "sku": "PD-DENT"
})
print("Product 3:", p3["product_name"], "(id=" + str(p3["id"]) + ")")

# 3. Add inventory
print("\n=== ADD INVENTORY ===")
i1 = post(BASE + "/inventory", {
    "product_id": p1["id"],
    "current_stock": 50,
    "reorder_level": 15,
    "unit": "pcs"
})
print("Inventory for product", i1["product_id"], "- stock:", i1["current_stock"])

i2 = post(BASE + "/inventory", {
    "product_id": p2["id"],
    "current_stock": 8,
    "reorder_level": 20,
    "unit": "pcs"
})
print("Inventory for product", i2["product_id"], "- stock:", i2["current_stock"])

i3 = post(BASE + "/inventory", {
    "product_id": p3["id"],
    "current_stock": 100,
    "reorder_level": 25,
    "unit": "pcs"
})
print("Inventory for product", i3["product_id"], "- stock:", i3["current_stock"])

# 4. RFID scan (simulates a sale)
print("\n=== RFID SCAN ===")
scan = post(BASE + "/rfid-scan", {
    "product_id": p2["id"],
    "event_type": "SALE",
    "rfid_tag_id": "TAG-001"
})
print("RFID:", scan["event_type"], "for", scan["product_name"])
print("  Stock after scan:", scan["current_stock"])
print("  Alert:", scan["stock_alert"])

# 5. Low stock alerts
print("\n=== LOW STOCK ALERTS ===")
alerts = get(BASE + "/inventory/low-stock")
for a in alerts:
    print("  LOW:", a["product_name"], "-",
          str(a["current_stock"]) + "/" + str(a["reorder_level"]),
          "(deficit:", str(a["deficit"]) + ")")

# 6. Create an order
print("\n=== CREATE ORDER ===")
order = post(BASE + "/orders", {
    "customer_name": "Rahul Sharma",
    "customer_phone": "+91-9876543210",
    "customer_address": "123 MG Road, Bengaluru",
    "delivery_slot": "10:00-11:00",
    "items": [
        {"product_id": p1["id"], "quantity": 2},
        {"product_id": p3["id"], "quantity": 3}
    ]
})
print("Order #" + str(order["id"]) + ":", order["customer_name"])
print("  Total: Rs." + str(order["total_amount"]))
print("  Status:", order["status"])
for item in order["items"]:
    print("  -", item["product_name"], "x" + str(item["quantity"]),
          "= Rs." + str(item["subtotal"]))

# 7. Update order status
print("\n=== UPDATE ORDER STATUS ===")
updated = patch(BASE + "/orders/" + str(order["id"]) + "/status", {
    "status": "confirmed"
})
print("Order #" + str(updated["id"]), "status:", updated["status"])

# 8. Store settings
print("\n=== STORE SETTINGS ===")
store_data = get(BASE + "/store")
print("Store:", store_data["name"])
print("  Open:", store_data["is_open"])
print("  Hours:", store_data["opening_time"], "-", store_data["closing_time"])

# 9. Analytics dashboard
print("\n=== ANALYTICS DASHBOARD ===")
dash = get(BASE + "/analytics/dashboard")
print("Revenue today: Rs." + str(dash["today_revenue"]))
print("Orders today:", dash["today_orders"])
print("Pending orders:", dash["pending_orders"])
print("Low stock items:", dash["low_stock_count"])
print("Active products:", dash["active_products"])
print("Fulfillment rate:", str(dash["fulfillment_rate"]) + "%")

# 10. Demand forecast
print("\n=== DEMAND FORECAST ===")
fc = get(BASE + "/forecast/" + str(p1["id"]))
print("Product", fc["product_id"], "- demand:", fc["predicted_demand_next_week"], "/week")
print("  Category:", fc["demand_category"])
print("  Explanation:", fc["explanation"])

# 11. Reorder optimization
print("\n=== REORDER OPTIMIZATION ===")
opt = get(BASE + "/optimize-reorder/" + str(p2["id"]))
print("Product", opt["product_id"], "- stock:", opt["current_stock"], "- risk:", opt["risk_level"])
print("  Recommend ordering:", opt["recommended_reorder_quantity"], "units")
print("  Explanation:", opt["explanation"])

# 12. RFID stats
print("\n=== RFID STATS ===")
stats = get(BASE + "/rfid-events/stats")
print("Total events:", stats["total_events"])
print("Sales:", stats["sale_count"])
print("Restocks:", stats["restock_count"])

# 13. Categories
print("\n=== PRODUCT CATEGORIES ===")
cats = get(BASE + "/products/categories")
print("Categories:", cats)

# 14. Order summary
print("\n=== ORDER SUMMARY ===")
summary = get(BASE + "/orders/summary")
print("Pending:", summary["pending"])
print("Confirmed:", summary["confirmed"])
print("Total:", summary["total"])

print("\n" + "=" * 50)
print("ALL ENDPOINTS TESTED SUCCESSFULLY!")
print("=" * 50)
