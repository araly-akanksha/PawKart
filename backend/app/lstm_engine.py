"""
Pure-NumPy LSTM Inference Engine
=================================
Loads weights directly from a Keras .keras (zip) model file
and runs LSTM inference without TensorFlow.

Architecture (from training script):
  LSTM(64, return_sequences=True) → Dropout(0.2)
  → LSTM(64) → Dropout(0.2)
  → Dense(1)

Input: (1, 30, 1) — 30-day sales sequence
Output: (1, 1)    — next-day predicted sales (scaled)
"""

import os
import io
import zipfile
import logging
import numpy as np
import h5py

logger = logging.getLogger(__name__)


def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-np.clip(x, -500, 500)))


def tanh(x):
    return np.tanh(x)


def lstm_cell_forward(x_t, h_prev, c_prev, W_x, W_h, b):
    """
    Single LSTM cell forward pass.
    
    Keras stores LSTM weights as:
      kernel (W_x):         shape (input_dim, 4*units)  — input weights
      recurrent_kernel (W_h): shape (units, 4*units)    — hidden weights  
      bias (b):             shape (4*units,)            — biases
    
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
    Returns: h at each timestep or just the last h
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


class NumpyLSTMModel:
    """
    Loads and runs inference for the PawKart LSTM demand forecasting model.
    """
    
    def __init__(self, model_path: str):
        self.model_path = model_path
        self.weights = {}
        self._load_weights()
    
    def _load_weights(self):
        """Extract weights from .keras zip file."""
        with zipfile.ZipFile(self.model_path, 'r') as z:
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
        
        logger.info(
            "Loaded LSTM weights: LSTM1(%s), LSTM2(%s), Dense(%s)",
            self.weights['lstm1_W_x'].shape,
            self.weights['lstm2_W_x'].shape,
            self.weights['dense_W'].shape,
        )
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Run forward pass.
        
        X: shape (batch_size, 30, 1) — scaled sales sequence
        Returns: shape (batch_size, 1) — predicted next-day scaled sales
        """
        # LSTM layer 1 (return_sequences=True)
        h1 = lstm_layer_forward(
            X,
            self.weights['lstm1_W_x'],
            self.weights['lstm1_W_h'],
            self.weights['lstm1_b'],
            return_sequences=True,
        )
        # Dropout is only applied during training — skip during inference
        
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
        
        return output  # (batch_size, 1)


def load_model(model_path: str) -> NumpyLSTMModel:
    """Load the LSTM model from a .keras file."""
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model not found at {model_path}")
    
    model = NumpyLSTMModel(model_path)
    logger.info("NumPy LSTM model loaded successfully from %s", model_path)
    return model
