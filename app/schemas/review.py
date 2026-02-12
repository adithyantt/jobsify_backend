from pydantic import BaseModel, field_serializer
from typing import Optional
from datetime import datetime


class ReviewBase(BaseModel):
    worker_id: int
    rating: int  # 1-5 stars
    comment: Optional[str] = None


class ReviewCreate(ReviewBase):
    # Only worker_id, rating, and comment are required from frontend
    # reviewer_email and reviewer_name come from JWT token (current_user)
    pass



class ReviewResponse(ReviewBase):
    id: int
    reviewer_email: str
    reviewer_name: Optional[str]
    created_at: Optional[str] = None

    class Config:
        from_attributes = True
    
    @field_serializer('created_at', mode='wrap')
    def serialize_created_at(self, value, handler):
        # Handle both datetime objects and strings
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.isoformat()
        return str(value)




class ReviewWithWorker(ReviewResponse):
    worker_name: Optional[str] = None
    worker_role: Optional[str] = None


class WorkerRatingSummary(BaseModel):
    average_rating: float
    total_reviews: int
    rating_distribution: dict  # {5: 10, 4: 5, 3: 2, 2: 1, 1: 0}
