from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index
from datetime import datetime, timezone
from app.database import Base


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    worker_id = Column(Integer, ForeignKey("workers.id"), nullable=False, index=True)
    reviewer_email = Column(String, nullable=False, index=True)
    reviewer_name = Column(String, nullable=True)
    rating = Column(Integer, nullable=False, index=True)
    comment = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    __table_args__ = (
        Index('idx_reviews_worker_rating', 'worker_id', 'rating'),
    )
    
    def to_dict(self):
        return {
            "id": self.id,
            "worker_id": self.worker_id,
            "reviewer_email": self.reviewer_email,
            "reviewer_name": self.reviewer_name,
            "rating": self.rating,
            "comment": self.comment,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

    @property
    def created_at_str(self):
        """Return created_at as ISO format string for JSON serialization"""
        if self.created_at:
            if isinstance(self.created_at, str):
                return self.created_at
            return self.created_at.isoformat()
        return None
