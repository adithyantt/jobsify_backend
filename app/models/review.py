from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from app.database import Base


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    worker_id = Column(Integer, ForeignKey("workers.id"), nullable=False)
    reviewer_email = Column(String, nullable=False)  # Email of user who gave review
    reviewer_name = Column(String, nullable=True)     # Name of reviewer
    rating = Column(Integer, nullable=False)          # 1-5 star rating
    comment = Column(String, nullable=True)           # Review text
    created_at = Column(DateTime, default=datetime.utcnow)
    
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
