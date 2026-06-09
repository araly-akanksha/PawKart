"""
NumPy LSTM Forecasting Model
=============================
Wraps the pure-NumPy LSTM engine in the ForecastModel interface.
Loads weights from Keras .keras zip files and performs scaled/unscaled predictions.
"""

import os
import io
import zipfile
import logging
from typing import Optional
import numpy as np
import h5py
import joblib

from app.ai.base import ForecastModel, ModelMetadata

logger = logging.getLogger(__name__)


# ── NumPy LSTM Layer Functions ─────────────────────────────────

def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-np.clip(x, -500, 500)))


def tanh(x):
    return np.tanh(x)


def lstm_cell_forward(x_t, h_prev, c_prev, W_x, W_h, b):
    """
    Single LSTM cell forward pass.
    Gate order in Keras: [i, f, c, o] (input, forget, cell, output)
    """
    units = h_prev.shape[-1]
    
    # Combined gate computation
    z = x_t @ W_x + h_prev @ W_h + b
    
    # Split into 4 gates
    i = sigmoid(z[:, 0:units])         # input gate
    f = sigmoid(z[:, units:2*units])   # forget gate
    c_tilde = tanh(z[:, 2*units:3*units])  # cell candidate
    o = sigmoid(z[:, 3*units:4*units]) # output gate
    
    # Update cell state and hidden state
    c_next = f * c_prev + i * c_tilde
    h_next = o * tanh(c_next)
    
    return h_next, c_next


def lstm_layer_forward(X, W_x, W_h, b, return_sequences=False):
    """
    Full LSTM layer forward pass over all timesteps.
    X: shape (batch_size, timesteps, features)
    """
    batch_size, timesteps, _ = X.shape
    units = W_h.shape[0]
    
    h = np.zeros((batch_size, units))
    c = np.zeros((batch_size, units))
    
    all_h = []
    
    for t in range(timesteps):
        x_t = X[:, t, :]
        h, c = lstm_cell_forward(x_t, h, c, W_x, W_h, b)
        if return_sequences:
            all_h.append(h.copy())
    
    if return_sequences:
        return np.stack(all_h, axis=1)  # (batch, timesteps, units)
    return h  # (batch, units)


# ── LSTM Model Wrapper Class ────────────────────────────────────

class LstmForecastModel(ForecastModel):
    """LSTM Forecasting Model implementing the ForecastModel interface."""

    def __init__(self):
        super().__init__(model_type="lstm")
        self.weights = {}
        self._scaler = None
        self.metadata.description = (
            "2-Layer LSTM Neural Network. Pure-NumPy implementation "
            "compatible with Keras weights."
        )
        self.metadata.input_type = "sequence"
        self.metadata.sequence_length = 30
        self.metadata.feature_names = ["total_sales"]

    def load(self, model_path: str, scaler_path: Optional[str] = None) -> None:
        """Load LSTM weights from Keras .keras file and load MinMaxScaler scaler."""
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found at: {model_path}")

        try:
            with zipfile.ZipFile(model_path, 'r') as z:
                with z.open('model.weights.h5') as f:
                    data = f.read()
                
                with h5py.File(io.BytesIO(data), 'r') as hf:
                    # LSTM layer 1 (return_sequences=True)
                    self.weights['lstm1_W_x'] = np.array(hf['layers/lstm/cell/vars/0'])      # (1, 256)
                    self.weights['lstm1_W_h'] = np.array(hf['layers/lstm/cell/vars/1'])      # (64, 256)
                    self.weights['lstm1_b']   = np.array(hf['layers/lstm/cell/vars/2'])      # (256,)
                    
                    # LSTM layer 2
                    self.weights['lstm2_W_x'] = np.array(hf['layers/lstm_1/cell/vars/0'])    # (64, 256)
                    self.weights['lstm2_W_h'] = np.array(hf['layers/lstm_1/cell/vars/1'])    # (64, 256)
                    self.weights['lstm2_b']   = np.array(hf['layers/lstm_1/cell/vars/2'])    # (256,)
                    
                    # Dense output layer
                    self.weights['dense_W']   = np.array(hf['layers/dense/vars/0'])          # (64, 1)
                    self.weights['dense_b']   = np.array(hf['layers/dense/vars/1'])          # (1,)

            self._loaded = True
            logger.info("LSTM model weights loaded successfully from %s", model_path)
        except Exception as e:
            self._loaded = False
            logger.error("Failed to load LSTM weights: %s", e)
            raise RuntimeError(f"Error loading LSTM model: {e}")

        # Load Scaler if path is provided
        if scaler_path:
            if not os.path.exists(scaler_path):
                logger.warning("Scaler file not found at: %s", scaler_path)
            else:
                try:
                    self._scaler = joblib.load(scaler_path)
                    logger.info("MinMaxScaler loaded successfully for LSTM model from %s", scaler_path)
                except Exception as e:
                    logger.error("Failed to load scaler: %s", e)
                    raise RuntimeError(f"Error loading scaler: {e}")

    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Run forward pass on SCALED input data.
        X shape: (batch_size, sequence_length, features) -> typically (batch_size, 30, 1)
        Returns: scaled prediction, shape (batch_size, 1)
        """
        if not self._loaded:
            raise RuntimeError("LSTM model has not been loaded. Call load() first.")

        # LSTM layer 1 (return_sequences=True)
        h1 = lstm_layer_forward(
            X,
            self.weights['lstm1_W_x'],
            self.weights['lstm1_W_h'],
            self.weights['lstm1_b'],
            return_sequences=True,
        )
        
        # LSTM layer 2 (return_sequences=False)
        h2 = lstm_layer_forward(
            h1,
            self.weights['lstm2_W_x'],
            self.weights['lstm2_W_h'],
            self.weights['lstm2_b'],
            return_sequences=False,
        )
        
        # Dense layer
        output = h2 @ self.weights['dense_W'] + self.weights['dense_b']
        return output

    def predict_with_inverse(self, X: np.ndarray) -> np.ndarray:
        """
        Predict and inverse-transform to original scale.
        X shape: (batch_size, sequence_length, features) in ORIGINAL scale.
        Returns: actual sales predictions in ORIGINAL scale, shape (batch_size, 1).
        """
        if self._scaler is None:
            raise RuntimeError("Scaler is not loaded. Cannot run predict_with_inverse().")

        # X is (batch_size, timesteps, features). Let's reshape to fit scaler transform
        batch_size, timesteps, features = X.shape
        X_flat = X.reshape(-1, features)
        
        # Scale
        X_scaled_flat = self._scaler.transform(X_flat)
        X_scaled = X_scaled_flat.reshape(batch_size, timesteps, features)
        
        # Run prediction
        pred_scaled = self.predict(X_scaled)
        
        # Inverse transform prediction
        pred_actual = self._scaler.inverse_transform(pred_scaled)
        return pred_actual
