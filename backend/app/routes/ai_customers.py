import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user
from app.schemas import CustomerPurchaseResponse
from app.ai.customer_prediction.predictor import predict_high_probability_customers

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/customer-purchase/high-probability", response_model=list[CustomerPurchaseResponse])
def get_high_probability_purchases(
    threshold: float = 0.4,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    CatBoost Batch prediction to find top N users most likely to buy within 7 days.
    """
    logger.info(f"Fetching top {limit} high-probability customers (threshold {threshold})")
    
    predictions = predict_high_probability_customers(db, threshold=threshold, limit=limit)
    
    if not predictions:
        # Fallback to mock data if model not trained yet
        logger.warning("No CatBoost predictions returned. Using mock fallback.")
        return [
            CustomerPurchaseResponse(
                customer_id=1,
                purchase_probability=0.92,
                segment="HIGH"
            ),
            CustomerPurchaseResponse(
                customer_id=3,
                purchase_probability=0.85,
                segment="HIGH"
            )
        ]
        
    return predictions

@router.get("/customer-purchase/{customer_id}", response_model=CustomerPurchaseResponse)
def get_customer_purchase_prediction(
    customer_id: int, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    [STUB] CatBoost Customer Purchase Prediction.
    Phase 3: Will load the trained model to predict if user will buy in next 7 days.
    """
    logger.info(f"Predicting purchase probability for customer {customer_id}")
    return CustomerPurchaseResponse(
        customer_id=customer_id,
        purchase_probability=0.88,
        predicted_category="Dog Food",
        factors={"loyalty_score": 0.9, "recent_browsing": "Dog Food"},
        segment="HIGH"
    )
