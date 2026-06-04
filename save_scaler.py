"""
Save the MinMaxScaler used during LSTM training.
The scaler was never persisted, so we re-fit it from
the same dataset to get identical scaling parameters.

Run: cd PawKart && python save_scaler.py
"""
import pandas as pd
import joblib
from sklearn.preprocessing import MinMaxScaler

# Load the same dataset used for training
df = pd.read_csv("demand_forecasting_dataset.csv")
sales_data = df[["total_sales"]]

# Re-fit the scaler with identical parameters
scaler = MinMaxScaler(feature_range=(0, 1))
scaler.fit(sales_data)

# Verify
print(f"Scaler min: {scaler.data_min_[0]}")
print(f"Scaler max: {scaler.data_max_[0]}")
print(f"Scale: {scaler.scale_[0]}")

# Save
joblib.dump(scaler, "backend/demand_scaler.joblib")
print("\nScaler saved to backend/demand_scaler.joblib")
