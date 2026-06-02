from fastapi import FastAPI
from product_routes import router as product_router
from inventory_routes import router as inventory_router
from rfid_routes import router as rfid_router

app = FastAPI(
    title="PawKart API",
    version="1.0"
)

app.include_router(product_router)
app.include_router(inventory_router)
app.include_router(rfid_router)

@app.get("/")
def home():
    return {
        "message": "PawKart Backend Running"
    }