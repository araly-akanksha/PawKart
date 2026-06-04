"""Test the LSTM forecasting and optimization endpoints."""
import urllib.request
import json

BASE = "http://127.0.0.1:8000"

def get(path):
    r = urllib.request.urlopen(f"{BASE}{path}")
    return json.loads(r.read())

print("=" * 60)
print("STAGE 6: LSTM Forecast Test")
print("=" * 60)

try:
    result = get("/forecast/1")
    print(f"\nProduct ID: {result['product_id']}")
    print(f"Demand:     {result['predicted_demand_next_week']} units/week")
    print(f"Category:   {result['demand_category']}")
    print(f"Confidence: {result['confidence']}")
    print(f"\nExplanation:\n{result['explanation']}")
except Exception as e:
    print(f"Forecast error: {e}")

print("\n" + "=" * 60)
print("STAGE 7: Explainable AI Reorder Test")
print("=" * 60)

try:
    result = get("/optimize-reorder/1")
    print(f"\nProduct ID:     {result['product_id']}")
    print(f"Current Stock:  {result['current_stock']}")
    print(f"Demand:         {result['predicted_demand']}")
    print(f"Reorder Qty:    {result['recommended_reorder_quantity']}")
    print(f"Risk Level:     {result['risk_level']}")
    print(f"\nExplanation:\n{result['explanation']}")
except Exception as e:
    print(f"Reorder error: {e}")

# Test a second product too
print("\n" + "=" * 60)
print("FORECAST for Product #5")
print("=" * 60)

try:
    result = get("/forecast/5")
    print(f"Demand: {result['predicted_demand_next_week']} units/week")
    print(f"Category: {result['demand_category']}")
    print(f"Confidence: {result['confidence']}")
    print(f"\n{result['explanation']}")
except Exception as e:
    print(f"Error: {e}")
