"""Diagnose forecast endpoint issue."""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import urllib.request
import json

BASE = "http://127.0.0.1:8000"

def get(path):
    try:
        r = urllib.request.urlopen(f"{BASE}{path}")
        return json.loads(r.read()), r.status
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        return json.loads(body) if body else {}, e.code

# 1. Health check
data, code = get("/")
print(f"1. Root endpoint: {code} — {data}")

# 2. Products check
data, code = get("/products")
print(f"2. Products: {code} — count: {len(data) if isinstance(data, list) else 'N/A'}")

if isinstance(data, list) and len(data) > 0:
    pid = data[0]["id"]
    name = data[0]["product_name"]
    print(f"   First product: id={pid}, name={name}")
    
    # 3. Forecast for first product
    data, code = get(f"/forecast/{pid}")
    print(f"3. Forecast (product {pid}): {code}")
    if code == 200:
        print(f"   Demand: {data['predicted_demand_next_week']} units/week")
        print(f"   Category: {data['demand_category']}")
        print(f"   Confidence: {data['confidence']}")
        print(f"   Explanation: {data['explanation'][:120]}...")
    else:
        print(f"   Error: {data}")
    
    # 4. Optimization for first product
    data, code = get(f"/optimize-reorder/{pid}")
    print(f"4. Reorder (product {pid}): {code}")
    if code == 200:
        print(f"   Risk: {data['risk_level']}")
        print(f"   Reorder: {data['recommended_reorder_quantity']} units")
    else:
        print(f"   Error: {data}")
else:
    print("   NO PRODUCTS IN DATABASE — run seed_data.py first")

# 5. Check 404 for nonexistent product
data, code = get("/forecast/99999")
print(f"5. Forecast (nonexistent): {code} — {data}")
