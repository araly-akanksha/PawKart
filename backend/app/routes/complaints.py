from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.dependencies import get_db, get_current_user
from app.models import Complaint, User
from app.schemas import ComplaintResponse, ComplaintCreate

router = APIRouter()

@router.get("/complaints", response_model=List[ComplaintResponse])
def get_complaints(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Complaint).all()

@router.post("/complaints", response_model=ComplaintResponse)
def create_complaint(complaint_in: ComplaintCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_complaint = Complaint(
        customer_email=complaint_in.customer_email,
        order_id=complaint_in.order_id,
        issue_description=complaint_in.issue_description,
        status="open"
    )
    db.add(new_complaint)
    db.commit()
    db.refresh(new_complaint)
    return new_complaint

@router.patch("/complaints/{complaint_id}")
def update_complaint_status(complaint_id: int, status: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    complaint.status = status
    db.commit()
    return {"message": "Status updated successfully", "status": status}
