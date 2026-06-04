# ============================================================
# PAWKART API — Main Application
# ============================================================
#
# AI-Driven Omnichannel Inventory & Quick-Commerce System
# for Independent Pet Stores
#
# Run with: uvicorn app.main:app --reload
# Swagger UI: http://localhost:8000/docs
# ============================================================

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.routes import products, inventory, rfid, orders, store, analytics
from app.routes import forecasting, optimization


# ── Lifespan: create tables on startup ───────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create all database tables
    Base.metadata.create_all(bind=engine)
    print("Database tables created/verified.")
    yield
    # Shutdown: nothing to clean up


# ── FastAPI Application ──────────────────────────────────────

app = FastAPI(
    title="PawKart API",
    description=(
        "AI-Driven Omnichannel Inventory & Quick-Commerce System "
        "for Independent Pet Stores. Features real-time RFID inventory "
        "tracking, demand forecasting, intelligent replenishment, "
        "and quick-commerce order fulfillment."
    ),
    version="2.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── CORS Middleware (for future React frontend) ──────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register Routers with Tags ───────────────────────────────

app.include_router(
    products.router,
    tags=["Products"]
)

app.include_router(
    inventory.router,
    tags=["Inventory"]
)

app.include_router(
    rfid.router,
    tags=["RFID"]
)

app.include_router(
    orders.router,
    tags=["Orders"]
)

app.include_router(
    store.router,
    tags=["Store"]
)

app.include_router(
    analytics.router,
    tags=["Analytics"]
)

app.include_router(
    forecasting.router,
    tags=["Forecasting"]
)

app.include_router(
    optimization.router,
    tags=["Optimization"]
)


# ── Health Check ─────────────────────────────────────────────

@app.get("/", tags=["Health"])
def home():
    return {
        "message": "PawKart Backend Running",
        "version": "2.0",
        "docs": "/docs"
    }


@app.get("/healthz", tags=["Health"])
def health_check():
    return {"status": "healthy"}
