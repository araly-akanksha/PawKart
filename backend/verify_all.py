"""
Full end-to-end verification of all API endpoints and data flow.
Tests every endpoint the frontend pages depend on.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import urllib.request
import json
import time

BASE = "http://127.0.0.1:8000"
passed = 0
failed = 0

def get(path):
    r = urllib.request.urlopen(f"{BASE}{path}")
    return json.loads(r.read()), r.status

def post(path, data):
    req = urllib.request.Request(
        f"{BASE}{path}",
        data=json.dumps(data).encode(),
        headers={"Content-Type": "application/json"},
    )
    r = urllib.request.urlopen(req)
    return json.loads(r.read()), r.status

def test(name, fn):
    global passed, failed
    try:
        fn()
        print(f"  PASS  {name}")
        passed += 1
    except Exception as e:
        print(f"  FAIL  {name}: {e}")
        failed += 1

print("=" * 60)
print("PAWKART FULL VERIFICATION")
print("=" * 60)

# ── Dashboard Page Dependencies ──────────────────────────────
print("\n1. Dashboard Page")

def t_dashboard():
    d, s = get("/analytics/dashboard")
    assert s == 200
    assert "today_revenue" in d
    assert "low_stock_count" in d
    assert "active_products" in d
    assert d["active_products"] == 25
test("GET /analytics/dashboard", t_dashboard)

def t_sales():
    d, s = get("/analytics/sales")
    assert s == 200
    assert isinstance(d, list)
    assert len(d) == 30
    assert "date" in d[0] and "revenue" in d[0]
test("GET /analytics/sales (30 days)", t_sales)

def t_order_summary():
    d, s = get("/orders/summary")
    assert s == 200
    assert d["total"] == 35
test("GET /orders/summary", t_order_summary)

# ── Products Page Dependencies ───────────────────────────────
print("\n2. Products Page")

def t_products():
    d, s = get("/products")
    assert s == 200 and len(d) == 25
test("GET /products (25 items)", t_products)

def t_categories():
    d, s = get("/products/categories")
    assert s == 200 and len(d) == 8
test("GET /products/categories (8 cats)", t_categories)

def t_product_filter():
    d, s = get("/products?category=Dog%20Food")
    assert s == 200 and len(d) == 5
test("GET /products?category=Dog Food (5)", t_product_filter)

def t_product_detail():
    all_p, _ = get("/products")
    pid = all_p[0]["id"]
    d, s = get(f"/products/{pid}")
    assert s == 200 and d["id"] == pid
test("GET /products/{id}", t_product_detail)

# ── Inventory Page Dependencies ──────────────────────────────
print("\n3. Inventory Page")

def t_inventory():
    d, s = get("/inventory")
    assert s == 200 and len(d) == 25
test("GET /inventory (25 records)", t_inventory)

def t_low_stock():
    d, s = get("/inventory/low-stock")
    assert s == 200 and isinstance(d, list)
test("GET /inventory/low-stock", t_low_stock)

# ── Orders Page Dependencies ─────────────────────────────────
print("\n4. Orders Page")

def t_orders():
    d, s = get("/orders")
    assert s == 200 and len(d) == 35
test("GET /orders (35 orders)", t_orders)

def t_orders_filter():
    d, s = get("/orders?status=delivered")
    assert s == 200
test("GET /orders?status=delivered", t_orders_filter)

# ── RFID Page Dependencies ───────────────────────────────────
print("\n5. RFID Page")

def t_rfid_stats():
    d, s = get("/rfid-events/stats")
    assert s == 200
    assert d["total_events"] == 60
test("GET /rfid-events/stats", t_rfid_stats)

def t_rfid_latest():
    d, s = get("/rfid-events/latest?count=20")
    assert s == 200 and len(d) <= 20
test("GET /rfid-events/latest", t_rfid_latest)

# ── AI Forecast Page Dependencies ────────────────────────────
print("\n6. AI Forecast Page")

def t_forecast():
    all_p, _ = get("/products")
    pid = all_p[0]["id"]
    d, s = get(f"/forecast/{pid}")
    assert s == 200
    assert "predicted_demand_next_week" in d
    assert "demand_category" in d
    assert "explanation" in d
    assert d["confidence"] in ("high", "medium", "low")
test("GET /forecast/{id} (LSTM)", t_forecast)

def t_reorder():
    all_p, _ = get("/products")
    pid = all_p[0]["id"]
    d, s = get(f"/optimize-reorder/{pid}")
    assert s == 200
    assert "risk_level" in d
    assert "explanation" in d
test("GET /optimize-reorder/{id}", t_reorder)

# ── Analytics Page Dependencies ──────────────────────────────
print("\n7. Analytics Page")

def t_fulfillment():
    d, s = get("/analytics/fulfillment")
    assert s == 200
    assert "fulfillment_rate" in d
    assert "cancel_rate" in d
    assert "on_time_rate" in d
    assert "avg_delivery_minutes" in d
test("GET /analytics/fulfillment", t_fulfillment)

def t_top_products():
    d, s = get("/analytics/top-products")
    assert s == 200
    assert len(d) <= 5
    if d:
        assert "total_sold" in d[0]
        assert "revenue" in d[0]
test("GET /analytics/top-products", t_top_products)

# ── Settings Page Dependencies ───────────────────────────────
print("\n8. Settings Page")

def t_store():
    d, s = get("/store")
    assert s == 200
    assert d["name"] == "PawKart Pet Store"
test("GET /store", t_store)

# ── Health ───────────────────────────────────────────────────
print("\n9. Health Check")

def t_health():
    d, s = get("/healthz")
    assert s == 200 and d["status"] == "healthy"
test("GET /healthz", t_health)

# ── CORS Header Check ───────────────────────────────────────
print("\n10. CORS Verification")

def t_cors():
    req = urllib.request.Request(
        f"{BASE}/products",
        headers={"Origin": "http://localhost:5173"},
    )
    r = urllib.request.urlopen(req)
    cors = r.headers.get("Access-Control-Allow-Origin", "")
    assert cors in ("*", "http://localhost:5173"), f"No CORS header, got '{cors}'"
test("CORS header present", t_cors)

# ── Results ──────────────────────────────────────────────────
print("\n" + "=" * 60)
print(f"RESULTS: {passed} passed, {failed} failed")
print("=" * 60)
if failed == 0:
    print("ALL TESTS PASSED")
else:
    print(f"WARNING: {failed} test(s) failed!")
