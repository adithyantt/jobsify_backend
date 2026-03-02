from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional

from app.database import get_db
from app.models.review import Review
from app.models.workers import Worker
from app.schemas.review import ReviewCreate, ReviewResponse, WorkerRatingSummary
from app.routers.auth import get_current_user, verify_token
from app.models.user import User
from fastapi.security import HTTPBearer

router = APIRouter(prefix="/reviews", tags=["Reviews"])
security = HTTPBearer(auto_error=False)


# =====================================================
# ⭐ GET REVIEWS FOR A WORKER
# =====================================================
@router.get("/worker/{worker_id}", response_model=list[ReviewResponse])
def get_worker_reviews(worker_id: int, db: Session = Depends(get_db)):
    """Get all reviews for a specific worker."""
    worker = db.query(Worker).filter(Worker.id == worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
    
    reviews = db.query(Review).filter(Review.worker_id == worker_id).order_by(Review.created_at.desc()).all()
    return [_review_to_dict(r) for r in reviews]


# =====================================================
# ⭐ GET WORKER RATING SUMMARY
# =====================================================
@router.get("/worker/{worker_id}/summary", response_model=WorkerRatingSummary)
def get_worker_rating_summary(worker_id: int, db: Session = Depends(get_db)):
    """Get rating summary for a worker."""
    worker = db.query(Worker).filter(Worker.id == worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
    
    distribution = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
    reviews = db.query(Review).filter(Review.worker_id == worker_id).all()
    
    for review in reviews:
        if review.rating in distribution:
            distribution[review.rating] += 1
    
    return WorkerRatingSummary(
        average_rating=worker.rating or 0.0,
        total_reviews=worker.reviews or 0,
        rating_distribution=distribution
    )


# =====================================================
# ⭐ HELPER: Get user email from request
# =====================================================
def get_user_email_from_request(
    request: Request,
    credentials = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
) -> str:
    """Get user email from JWT token header or email query parameter."""
    
    # First, try to get email from query parameter
    email = request.query_params.get("email")
    if email:
        return email
    
    # Try JWT token
    if credentials:
        try:
            payload = verify_token(credentials.credentials)
            user_email = payload.get("sub")
            if user_email:
                return user_email
        except:
            pass
    
    raise HTTPException(
        status_code=401, 
        detail="Authentication required. Please login or provide email parameter."
    )


# =====================================================
# ⭐ ADD A REVIEW
# =====================================================
@router.post("", response_model=ReviewResponse)
def create_review(
    review: ReviewCreate,
    user_email: str = Depends(get_user_email_from_request),
    db: Session = Depends(get_db)
):
    """Add a review for a worker."""
    
    print(f"DEBUG: create_review called by {user_email}")
    
    current_user = db.query(User).filter(User.email == user_email).first()
    if not current_user:
        raise HTTPException(status_code=401, detail="User not found. Please login.")
    
    if hasattr(current_user, 'blocked') and current_user.blocked:
        raise HTTPException(status_code=403, detail="Your account has been blocked.")
    
    worker = db.query(Worker).filter(Worker.id == review.worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
    
    existing_review = db.query(Review).filter(
        Review.worker_id == review.worker_id,
        Review.reviewer_email == user_email
    ).first()
    
    if existing_review:
        raise HTTPException(status_code=400, detail="You have already reviewed this worker.")
    
    if review.rating < 1 or review.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    
    try:
        new_review = Review(
            worker_id=review.worker_id,
            reviewer_email=user_email,
            reviewer_name=current_user.name or user_email,
            rating=review.rating,
            comment=review.comment
        )
        
        db.add(new_review)
        db.commit()
        db.refresh(new_review)
        
        _update_worker_rating(review.worker_id, db)
        return _review_to_dict(new_review)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create review: {str(e)}")


# =====================================================
# ⭐ UPDATE A REVIEW
# =====================================================
@router.put("/{review_id}", response_model=ReviewResponse)
def update_review(
    review_id: int,
    review_update: ReviewCreate,
    user_email: str = Depends(get_user_email_from_request),
    db: Session = Depends(get_db)
):
    """Update an existing review."""
    
    existing_review = db.query(Review).filter(Review.id == review_id).first()
    
    if not existing_review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    if existing_review.reviewer_email != user_email:
        raise HTTPException(status_code=403, detail="You can only update your own reviews")
    
    if review_update.rating < 1 or review_update.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    
    existing_review.rating = review_update.rating
    existing_review.comment = review_update.comment
    
    db.commit()
    db.refresh(existing_review)
    
    _update_worker_rating(existing_review.worker_id, db)
    return _review_to_dict(existing_review)


# =====================================================
# ⭐ DELETE A REVIEW
# =====================================================
@router.delete("/{review_id}")
def delete_review(
    review_id: int,
    user_email: str = Depends(get_user_email_from_request),
    db: Session = Depends(get_db)
):
    """Delete a review."""
    
    review = db.query(Review).filter(Review.id == review_id).first()
    
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    user = db.query(User).filter(User.email == user_email).first()
    is_admin = user and user.role == "admin" if user else False
    
    if review.reviewer_email != user_email and not is_admin:
        raise HTTPException(status_code=403, detail="You can only delete your own reviews")
    
    worker_id = review.worker_id
    db.delete(review)
    db.commit()
    
    _update_worker_rating(worker_id, db)
    return {"message": "Review deleted successfully"}


# =====================================================
# ⭐ GET MY REVIEWS
# =====================================================
@router.get("/my", response_model=list[ReviewResponse])
def get_my_reviews(
    user_email: str = Depends(get_user_email_from_request),
    db: Session = Depends(get_db)
):
    """Get all reviews given by the user."""
    
    print(f"DEBUG: get_my_reviews called by {user_email}")
    
    reviews = db.query(Review).filter(Review.reviewer_email == user_email).order_by(Review.created_at.desc()).all()
    return [_review_to_dict(r) for r in reviews]


# =====================================================
# 🔧 HELPER: Convert Review to Dict
# =====================================================
def _review_to_dict(review: Review) -> dict:
    return {
        "id": review.id,
        "worker_id": review.worker_id,
        "reviewer_email": review.reviewer_email,
        "reviewer_name": review.reviewer_name,
        "rating": review.rating,
        "comment": review.comment,
        "created_at": review.created_at.isoformat() if review.created_at else None
    }


# =====================================================
# 🔧 HELPER: Update Worker Rating
# =====================================================
def _update_worker_rating(worker_id: int, db: Session):
    reviews = db.query(Review).filter(Review.worker_id == worker_id).all()
    
    if not reviews:
        worker = db.query(Worker).filter(Worker.id == worker_id).first()
        if worker:
            worker.rating = 4.0
            worker.reviews = 0
            db.commit()
        return
    
    total_rating = sum(review.rating for review in reviews)
    average = total_rating / len(reviews)
    
    worker = db.query(Worker).filter(Worker.id == worker_id).first()
    if worker:
        worker.rating = round(average, 1)
        worker.reviews = len(reviews)
        db.commit()
