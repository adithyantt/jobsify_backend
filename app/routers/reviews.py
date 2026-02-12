from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from app.database import get_db
from app.models.review import Review
from app.models.workers import Worker
from app.schemas.review import ReviewCreate, ReviewResponse, WorkerRatingSummary
from app.routers.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/reviews", tags=["Reviews"])


# =====================================================
# ⭐ GET REVIEWS FOR A WORKER
# =====================================================
@router.get("/worker/{worker_id}", response_model=list[ReviewResponse])
def get_worker_reviews(worker_id: int, db: Session = Depends(get_db)):
    """Get all reviews for a specific worker."""
    # Check if worker exists
    worker = db.query(Worker).filter(Worker.id == worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
    
    reviews = (
        db.query(Review)
        .filter(Review.worker_id == worker_id)
        .order_by(Review.created_at.desc())
        .all()
    )
    
    # Convert reviews to dicts with proper datetime handling
    return [_review_to_dict(r) for r in reviews]



# =====================================================
# ⭐ GET WORKER RATING SUMMARY
# =====================================================
@router.get("/worker/{worker_id}/summary", response_model=WorkerRatingSummary)
def get_worker_rating_summary(worker_id: int, db: Session = Depends(get_db)):
    """Get rating summary for a worker including distribution."""
    worker = db.query(Worker).filter(Worker.id == worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
    
    # Get rating distribution
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
# ⭐ ADD A REVIEW (Authenticated)
# =====================================================
@router.post("", response_model=ReviewResponse)
def create_review(
    review: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add a review for a worker. User must be authenticated."""
    
    print(f"DEBUG: create_review called by {current_user.email}")
    print(f"DEBUG: review data: worker_id={review.worker_id}, rating={review.rating}")
    
    # Check if user is blocked
    if hasattr(current_user, 'blocked') and current_user.blocked:
        print(f"DEBUG: User {current_user.email} is blocked")
        raise HTTPException(status_code=403, detail="Your account has been blocked. Please contact support.")
    
    # Check if worker exists
    worker = db.query(Worker).filter(Worker.id == review.worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
    
    # Check if user already reviewed this worker
    existing_review = (
        db.query(Review)
        .filter(
            Review.worker_id == review.worker_id,
            Review.reviewer_email == current_user.email
        )
        .first()
    )
    
    if existing_review:
        print(f"DEBUG: User {current_user.email} already reviewed worker {review.worker_id}")
        raise HTTPException(
            status_code=400, 
            detail="You have already reviewed this worker. Please update your existing review."
        )
    
    # Validate rating
    if review.rating < 1 or review.rating > 5:
        print(f"DEBUG: Invalid rating: {review.rating}")
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    
    # Create new review
    try:
        new_review = Review(
            worker_id=review.worker_id,
            reviewer_email=current_user.email,
            reviewer_name=current_user.name or current_user.email,
            rating=review.rating,
            comment=review.comment
        )
        
        db.add(new_review)
        db.commit()
        db.refresh(new_review)
        
        print(f"DEBUG: Review created successfully: id={new_review.id}")
        
        # Update worker's average rating
        _update_worker_rating(review.worker_id, db)
        
        return _review_to_dict(new_review)
    except Exception as e:
        print(f"DEBUG: Error creating review: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create review: {str(e)}")




# =====================================================
# ⭐ UPDATE A REVIEW (Authenticated - Only reviewer)
# =====================================================
@router.put("/{review_id}", response_model=ReviewResponse)
def update_review(
    review_id: int,
    review_update: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an existing review. Only the reviewer can update."""
    
    existing_review = db.query(Review).filter(Review.id == review_id).first()
    
    if not existing_review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    # Check if current user is the reviewer
    if existing_review.reviewer_email != current_user.email:
        raise HTTPException(
            status_code=403, 
            detail="You can only update your own reviews"
        )
    
    # Validate rating
    if review_update.rating < 1 or review_update.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    
    # Update review
    existing_review.rating = review_update.rating
    existing_review.comment = review_update.comment
    
    db.commit()
    db.refresh(existing_review)
    
    # Update worker's average rating
    _update_worker_rating(existing_review.worker_id, db)
    
    return _review_to_dict(existing_review)



# =====================================================
# ⭐ DELETE A REVIEW (Authenticated - Only reviewer or admin)
# =====================================================
@router.delete("/{review_id}")
def delete_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a review. Reviewer or admin can delete."""
    
    review = db.query(Review).filter(Review.id == review_id).first()
    
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    # Check if current user is the reviewer or admin
    if review.reviewer_email != current_user.email and current_user.role != "admin":
        raise HTTPException(
            status_code=403, 
            detail="You can only delete your own reviews"
        )
    
    worker_id = review.worker_id
    
    db.delete(review)
    db.commit()
    
    # Update worker's average rating
    _update_worker_rating(worker_id, db)
    
    return {"message": "Review deleted successfully"}


# =====================================================
# ⭐ GET MY REVIEWS (Authenticated)
# =====================================================
@router.get("/my", response_model=list[ReviewResponse])
def get_my_reviews(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all reviews given by the current user."""
    
    reviews = (
        db.query(Review)
        .filter(Review.reviewer_email == current_user.email)
        .order_by(Review.created_at.desc())
        .all()
    )
    
    return [_review_to_dict(r) for r in reviews]



# =====================================================
# 🔧 HELPER: Convert Review to Dict (handle datetime)
# =====================================================
def _review_to_dict(review: Review) -> dict:
    """Convert Review object to dict with proper datetime handling."""
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

    """Recalculate and update worker's average rating."""
    
    reviews = db.query(Review).filter(Review.worker_id == worker_id).all()
    
    if not reviews:
        # No reviews, reset to default
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
