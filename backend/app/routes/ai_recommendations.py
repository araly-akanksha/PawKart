import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user
from app.schemas import CustomerRecommendationResponse, RecommendationItem

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/recommendations/customer/{customer_id}", response_model=CustomerRecommendationResponse)
def get_customer_recommendations(
    customer_id: int, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    [STUB] XGBoost Recommendation Engine.
    Increases basket value by suggesting frequently bought together items.
    """
    return CustomerRecommendationResponse(
        customer_id=customer_id,
        recommendations=[
            RecommendationItem(
                product_id=31,
                score=0.94,
                reason="Frequently purchased with Dog Food"
            ),
            RecommendationItem(
                product_id=15,
                score=0.82,
                reason="Top-selling in Grooming"
            )
        ]
    )
