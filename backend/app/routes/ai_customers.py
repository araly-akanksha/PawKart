import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user
from app.schemas import CustomerPurchaseResponse

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/customer-purchase/{customer_id}", response_model=CustomerPurchaseResponse)
def get_customer_purchase_prediction(
    customer_id: int, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    [STUB] CatBoost Customer Purchase Prediction.
    Predicts which customers are likely to purchase again.
    """
    return CustomerPurchaseResponse(
        customer_id=customer_id,
        purchase_probability=0.87,
        segment="HIGH"
    )

@router.get("/customer-purchase/high-probability", response_model=list[CustomerPurchaseResponse])
def get_high_probability_customers(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    [STUB] Get list of all HIGH segment customers.
    """
    return [
        CustomerPurchaseResponse(
            customer_id=120,
            purchase_probability=0.87,
            segment="HIGH"
        )
    ]
