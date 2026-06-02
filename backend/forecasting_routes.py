from fastapi import APIRouter
import random

router = APIRouter()

@router.get("/forecast/{product_id}")
def forecast_demand(product_id: int):

    predicted_demand = random.randint(50, 200)

    return {
        "product_id": product_id,
        "predicted_demand_next_week": predicted_demand
    }