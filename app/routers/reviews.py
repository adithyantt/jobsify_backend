from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
import logging

from app.database import get_db
from app.models.review import Review
from app.models.user import User
from app.models.workers import Worker
from app.schemas.review import ReviewCreate, ReviewUpdate, ReviewResponse, WorkerRatingSummary

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/reviews", tags=["Reviews"])


def _resolve_reviewer_name(user: User | None, reviewer_email: str) -> str:
    if user:
        return user.display_name
    if "@" in reviewer_email:
        return reviewer_email.split("@")[0]
    return reviewer_email or "User"


@router.get("/worker/{worker_id}", response_model=list[ReviewResponse])
def get_worker_reviews(worker_id: int, db: Session = Depends(get_db)):
    """Get all reviews for a specific worker."""
    worker = db.query(Worker).filter(Worker.id == worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")

    reviews = (
        db.query(Review)
        .filter(Review.worker_id == worker_id)
        .order_by(Review.created_at.desc())
        .all()
    )
    content = [_review_to_dict_with_user(review, db) for review in reviews]
    headers = {
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "Expires": "0",
    }
    return JSONResponse(content=content, headers=headers)


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

    content = WorkerRatingSummary(
        average_rating=worker.rating or 0.0,
        total_reviews=len(reviews),
        rating_distribution=distribution,
    ).model_dump()
    headers = {
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "Expires": "0",
    }
    return JSONResponse(content=content, headers=headers)


@router.post("", response_model=ReviewResponse)
def create_review(review: ReviewCreate, db: Session = Depends(get_db)):
    """Add a review for a worker (no authentication required)."""
    reviewer_email = review.reviewer_email.strip().lower()

    worker = db.query(Worker).filter(Worker.id == review.worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")

    existing_review = (
        db.query(Review)
        .filter(
            Review.worker_id == review.worker_id,
            func.lower(Review.reviewer_email) == reviewer_email,
        )
        .first()
    )
    if existing_review:
        raise HTTPException(status_code=400, detail="You have already reviewed this worker.")

    if review.rating < 1 or review.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")

    try:
        user = db.query(User).filter(func.lower(User.email) == reviewer_email).first()
        new_review = Review(
            worker_id=review.worker_id,
            reviewer_email=reviewer_email,
            reviewer_name=_resolve_reviewer_name(user, reviewer_email),
            rating=review.rating,
            comment=review.comment,
        )

        db.add(new_review)
        db.commit()
        db.refresh(new_review)

        _update_worker_rating(review.worker_id, db)
        return _review_to_dict(new_review)
    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create review: {str(exc)}")


@router.put("/{review_id}", response_model=ReviewResponse)
def update_review(
    review_id: int,
    review_update: ReviewUpdate,
    db: Session = Depends(get_db),
):
    """Update an existing review (no authentication required)."""
    logger.debug("Update review %s payload: %s", review_id, review_update.model_dump())

    existing_review = db.query(Review).filter(Review.id == review_id).first()
    if not existing_review:
        logger.error("Review %s not found", review_id)
        raise HTTPException(status_code=404, detail="Review not found")

    reviewer_email = (review_update.reviewer_email or existing_review.reviewer_email).strip().lower()
    if reviewer_email != existing_review.reviewer_email.lower():
        logger.warning("Unauthorized update attempt on review %s by %s", review_id, reviewer_email)
        raise HTTPException(status_code=403, detail="You can only update your own reviews")

    if review_update.rating is not None:
        if review_update.rating < 1 or review_update.rating > 5:
            logger.warning("Invalid rating %s for review %s", review_update.rating, review_id)
            raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
        existing_review.rating = review_update.rating

    if review_update.comment is not None:
        existing_review.comment = review_update.comment

    db.commit()
    db.refresh(existing_review)

    _update_worker_rating(existing_review.worker_id, db)
    logger.info("Updated review %s", review_id)
    return _review_to_dict(existing_review)


@router.delete("/{review_id}")
def delete_review(
    review_id: int,
    reviewer_email: str = Query(..., description="Email of the reviewer owning this review"),
    db: Session = Depends(get_db),
):
    """Delete a review (no authentication required)."""
    normalized_email = reviewer_email.strip().lower()
    logger.debug("Delete review %s by %s", review_id, normalized_email)

    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        logger.error("Review %s not found", review_id)
        raise HTTPException(status_code=404, detail="Review not found")

    if review.reviewer_email.lower() != normalized_email:
        logger.warning(
            "Unauthorized delete on review %s by %s, owner is %s",
            review_id,
            normalized_email,
            review.reviewer_email,
        )
        raise HTTPException(status_code=403, detail="You can only delete your own reviews")

    worker_id = review.worker_id
    db.delete(review)
    db.commit()

    _update_worker_rating(worker_id, db)
    logger.info("Deleted review %s", review_id)
    return {"message": "Review deleted successfully"}


@router.get("/my", response_model=list[ReviewResponse])
def get_my_reviews(
    reviewer_email: str = Query(...),
    db: Session = Depends(get_db),
):
    """Get all reviews given by the user."""
    normalized_email = reviewer_email.strip().lower()
    reviews = (
        db.query(Review)
        .filter(func.lower(Review.reviewer_email) == normalized_email)
        .order_by(Review.created_at.desc())
        .all()
    )
    content = [_review_to_dict(review) for review in reviews]
    headers = {
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "Expires": "0",
    }
    return JSONResponse(content=content, headers=headers)


def _review_to_dict(review: Review) -> dict:
    return {
        "id": review.id,
        "worker_id": review.worker_id,
        "reviewer_email": review.reviewer_email,
        "reviewer_name": review.reviewer_name,
        "rating": review.rating,
        "comment": review.comment,
        "created_at": review.created_at.isoformat() if review.created_at else None,
    }


def _review_to_dict_with_user(review: Review, db: Session) -> dict:
    reviewer_name = review.reviewer_name
    if not reviewer_name:
        user = db.query(User).filter(func.lower(User.email) == review.reviewer_email.lower()).first()
        reviewer_name = _resolve_reviewer_name(user, review.reviewer_email)

    return {
        "id": review.id,
        "worker_id": review.worker_id,
        "reviewer_email": review.reviewer_email,
        "reviewer_name": reviewer_name,
        "rating": review.rating,
        "comment": review.comment,
        "created_at": review.created_at.isoformat() if review.created_at else None,
    }


def _update_worker_rating(worker_id: int, db: Session):
    reviews = db.query(Review).filter(Review.worker_id == worker_id).all()

    worker = db.query(Worker).filter(Worker.id == worker_id).first()
    if not worker:
        return

    if not reviews:
        worker.rating = 0
        worker.reviews = 0
        db.commit()
        db.refresh(worker)
        return

    total_rating = sum(review.rating for review in reviews)
    average = total_rating / len(reviews)
    worker.rating = round(average, 1)
    worker.reviews = len(reviews)
    db.commit()
    db.refresh(worker)
