# ============================================================
# DEMAND FORECASTING USING LSTM
# ============================================================

# -----------------------------
# IMPORT LIBRARIES
# -----------------------------

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import mean_squared_error

from keras.models import Sequential
from keras.layers import LSTM, Dense, Dropout

# ============================================================
# LOAD FORECASTING DATASET
# ============================================================

df = pd.read_csv("demand_forecasting_dataset.csv")

print(df.head())

# ============================================================
# CONVERT DATE COLUMN
# ============================================================

df['date'] = pd.to_datetime(df['date'])

# SORT DATA

df = df.sort_values('date')

# ============================================================
# SELECT TARGET VARIABLE
# ============================================================

sales_data = df[['total_sales']]

# ============================================================
# NORMALIZE DATA
# ============================================================

scaler = MinMaxScaler(feature_range=(0, 1))

scaled_data = scaler.fit_transform(sales_data)

# ============================================================
# CREATE SEQUENCES FOR LSTM
# ============================================================

X = []
y = []

sequence_length = 30

for i in range(sequence_length, len(scaled_data)):
    
    X.append(scaled_data[i-sequence_length:i, 0])
    y.append(scaled_data[i, 0])

X = np.array(X)
y = np.array(y)

# RESHAPE FOR LSTM

X = np.reshape(
    X,
    (X.shape[0], X.shape[1], 1)
)

print("X Shape:", X.shape)
print("y Shape:", y.shape)

# ============================================================
# TRAIN TEST SPLIT
# ============================================================

split = int(0.8 * len(X))

X_train = X[:split]
X_test = X[split:]

y_train = y[:split]
y_test = y[split:]

# ============================================================
# BUILD LSTM MODEL
# ============================================================

model = Sequential()

# FIRST LSTM LAYER

model.add(
    LSTM(
        units=64,
        return_sequences=True,
        input_shape=(X_train.shape[1], 1)
    )
)

model.add(Dropout(0.2))

# SECOND LSTM LAYER

model.add(
    LSTM(
        units=64
    )
)

model.add(Dropout(0.2))

# OUTPUT LAYER

model.add(Dense(1))

# ============================================================
# COMPILE MODEL
# ============================================================

model.compile(
    optimizer='adam',
    loss='mean_squared_error'
)

# ============================================================
# TRAIN MODEL
# ============================================================

history = model.fit(
    X_train,
    y_train,
    epochs=20,
    batch_size=32,
    validation_data=(X_test, y_test)
)

# ============================================================
# MAKE PREDICTIONS
# ============================================================

predictions = model.predict(X_test)

# INVERSE TRANSFORM

predictions = scaler.inverse_transform(
    predictions.reshape(-1, 1)
)

y_test_actual = scaler.inverse_transform(
    y_test.reshape(-1, 1)
)

# ============================================================
# EVALUATE MODEL
# ============================================================

mae = mean_absolute_error(
    y_test_actual,
    predictions
)

rmse = np.sqrt(
    mean_squared_error(
        y_test_actual,
        predictions
    )
)

print("\n========================")
print("MODEL PERFORMANCE")
print("========================")

print("MAE:", mae)
print("RMSE:", rmse)

# ============================================================
# VISUALIZE RESULTS
# ============================================================

plt.figure(figsize=(14,6))

plt.plot(
    y_test_actual,
    label='Actual Sales'
)

plt.plot(
    predictions,
    label='Predicted Sales'
)

# ============================================================
# FUTURE DEMAND PREDICTION
# ============================================================

last_30_days = scaled_data[-30:]

future_input = np.reshape(
    last_30_days,
    (1, 30, 1)
)

future_prediction = model.predict(future_input)

future_prediction = scaler.inverse_transform(
    future_prediction
)

print("\n========================")
print("NEXT DAY DEMAND PREDICTION")
print("========================")

print("Predicted Future Sales:", future_prediction[0][0])

# ============================================================
# SAVE MODEL
# ============================================================

model.save("lstm_demand_forecasting_model.keras")

print("\nModel Saved Successfully")

# ============================================================
# SAVE PREDICTIONS
# ============================================================

prediction_results = pd.DataFrame({
    'Actual_Sales': y_test_actual.flatten(),
    'Predicted_Sales': predictions.flatten()
})

prediction_results.to_csv(
    "forecast_results.csv",
    index=False
)

print("\nForecast Results Saved")

# ============================================================
# DEMAND CATEGORY CLASSIFICATION
# ============================================================

def demand_category(sales):
    
    if sales > 500:
        return "High Demand"
    
    elif sales > 200:
        return "Medium Demand"
    
    else:
        return "Low Demand"

prediction_results['Demand_Category'] = (
    prediction_results['Predicted_Sales']
    .apply(demand_category)
)

print("\nDemand Categories:")
print(
    prediction_results.head()
)

# ============================================================
# END OF FORECASTING MODULE
# ============================================================