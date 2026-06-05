# 🐾 PawKart — AI-Powered Pet Store Inventory System

An AI-driven omnichannel inventory and quick-commerce platform for independent pet stores. Features LSTM-based demand forecasting, RFID inventory tracking, intelligent reorder optimization, and explainable AI.

## Architecture

```
PawKart/
├── backend/                 # FastAPI + PostgreSQL + SQLAlchemy
│   ├── app/
│   │   ├── main.py          # FastAPI app with CORS & routers
│   │   ├── models.py        # 6 SQLAlchemy models
│   │   ├── schemas.py       # Pydantic request/response schemas
│   │   ├── lstm_engine.py   # Pure-NumPy LSTM inference engine
│   │   └── routes/          # 8 route modules (29 endpoints)
│   ├── seed_data.py         # Database population script
│   └── demand_scaler.joblib # Fitted MinMaxScaler for LSTM
├── frontend/                # React + Vite
│   └── src/
│       ├── api.js           # API client (29 endpoint functions)
│       ├── pages/           # 8 dashboard pages
│       └── components/      # Sidebar + Layout
├── lstm_demand_forecasting_model.keras  # Trained LSTM model
└── demand_forecasting_dataset.csv       # 98,875 sales records
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI, Python 3.14, Uvicorn |
| Database | PostgreSQL, SQLAlchemy 2.0 |
| Frontend | React 19, Vite, Recharts, Lucide Icons |
| ML/AI | LSTM (2-layer, 64 units), NumPy inference engine |
| Data | MinMaxScaler (scikit-learn), h5py for model weights |

## Quick Start

### Prerequisites
- Python 3.10+ with pip
- Node.js 18+ with npm
- PostgreSQL (create a database named `pawkart_db`)

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv ../venv
../venv/Scripts/activate  # Windows
# source ../venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure database
# Edit .env with your PostgreSQL credentials:
# DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/pawkart_db

# Seed database with sample data
python seed_data.py

# Save LSTM scaler (one-time)
cd .. && python save_scaler.py && cd backend

# Start backend
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev -- --port 5173
```

### 3. Open Dashboard

- **Dashboard**: http://localhost:5173
- **API Docs**: http://localhost:8000/docs

## API Endpoints (29 total)

### Products (7)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/products` | List all products (optional `?category=`) |
| GET | `/products/categories` | List unique categories |
| GET | `/products/{id}` | Get product by ID |
| POST | `/products` | Create product |
| PUT | `/products/{id}` | Update product |
| DELETE | `/products/{id}` | Delete product |
| PATCH | `/products/{id}/availability` | Toggle availability |

### Inventory (5)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/inventory` | List all inventory |
| POST | `/inventory` | Create inventory record |
| PATCH | `/inventory/{product_id}` | Update inventory |
| PUT | `/inventory/update-stock` | Deduct stock (sale) |
| GET | `/inventory/low-stock` | Low stock alerts |

### RFID (4)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/rfid-scan` | Register RFID scan event |
| GET | `/rfid-events` | List events (with filters) |
| GET | `/rfid-events/latest` | Latest N events |
| GET | `/rfid-events/stats` | Event statistics |

### Orders (5)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/orders` | Create order |
| GET | `/orders` | List orders (optional `?status=`) |
| GET | `/orders/summary` | Status breakdown |
| GET | `/orders/{id}` | Order details |
| PATCH | `/orders/{id}/status` | Update order status |

### Store (2)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/store` | Get store profile |
| PATCH | `/store` | Update store profile |

### Analytics (4)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/analytics/dashboard` | Dashboard KPIs |
| GET | `/analytics/sales` | 30-day sales data |
| GET | `/analytics/fulfillment` | Fulfillment metrics |
| GET | `/analytics/top-products` | Top 5 products |

### AI / ML (2)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/forecast/{product_id}` | LSTM demand prediction |
| GET | `/optimize-reorder/{product_id}` | AI reorder recommendation |

## LSTM Demand Forecasting

The system uses a custom pure-NumPy LSTM inference engine that loads weights directly from the trained Keras model without requiring TensorFlow.

**Pipeline:**
1. Build 30-day sales sequence for a product from order history
2. Normalize using MinMaxScaler (fitted on 98,875 training records)
3. Feed through 2-layer LSTM (64 units each) + Dense(1) forward pass
4. Inverse-transform to get predicted daily sales in ₹
5. Classify demand level and generate explainable report

**Why NumPy instead of TensorFlow?**
TensorFlow does not yet support Python 3.14. The NumPy engine reads model weights directly from the `.keras` file via h5py and implements the exact LSTM math (sigmoid/tanh gates) — producing identical outputs.

## Dashboard Pages

| Page | Route | Features |
|------|-------|----------|
| Dashboard | `/` | KPI cards, 30-day sales chart, order status |
| Products | `/products` | Product table, category filter, add/delete, availability toggle |
| Inventory | `/inventory` | Stock table, low-stock alerts, AI reorder button |
| Orders | `/orders` | Order lifecycle, status badges, create order form |
| RFID Monitor | `/rfid` | Event stats, scan simulator, event table |
| AI Forecast | `/forecast` | LSTM prediction runner, demand chart, explainable AI panel |
| Analytics | `/analytics` | Fulfillment KPIs, revenue bar chart, top products |
| Settings | `/settings` | Store profile, open/close toggle, delivery config |

## Seed Data

Run `python seed_data.py` to populate:
- 25 pet products across 8 categories
- 25 inventory records with realistic stock levels
- 60 RFID events (last 14 days)
- 35 orders with 89 line items across 10 customers
- 1 store profile
