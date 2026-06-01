from fastapi import FastAPI
from product_routes import router as product_router

app = FastAPI(
    title="PawKart API",
    version="1.0"
)

app.include_router(product_router)


@app.get("/")
def home():
    return {
        "message": "PawKart Backend Running"
    }