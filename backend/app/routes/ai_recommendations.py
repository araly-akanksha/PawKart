import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user
from app.schemas import CustomerRecommendationResponse, RecommendationItem

from app.ai.recommendation.predictor import get_recommendations

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/recommendations/customer/{customer_id}", response_model=CustomerRecommendationResponse)
def get_customer_recommendations(
    customer_id: int, 
    limit: int = 4,
    db: Session = Depends(get_db)
):
    """
    XGBoost-powered product recommendations for a specific customer.
    """
    logger.info(f"Generating top {limit} recommendations for customer {customer_id}")
    
    recommendations = get_recommendations(customer_id, db, limit=limit)
    
    if not recommendations or not recommendations.recommendations:
        logger.warning(f"XGBoost returned no recommendations for customer {customer_id}. Using fallback.")
        return CustomerRecommendationResponse(
            customer_id=customer_id,
            recommendations=[
                RecommendationItem(product_id=1, score=0.95, reason="Trending in Dog Food"),
                RecommendationItem(product_id=5, score=0.88, reason="Popular with similar users"),
                RecommendationItem(product_id=12, score=0.82, reason="Frequently bought together")
            ]
        )
        
    return recommendations
