from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.database import Base

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String, index=True)  # Use email instead of id
    title = Column(String, nullable=False)
    message = Column(String, nullable=False)
    type = Column(String, nullable=True)  # job, worker, report, account
    reference_id = Column(Integer, nullable=True)  # ID of related content
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
