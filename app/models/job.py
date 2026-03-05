from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from datetime import datetime
from app.database import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    category = Column(String, nullable=False)
    description = Column(String, nullable=False)
    location = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    latitude = Column(String, nullable=True)
    longitude = Column(String, nullable=True)
    user_email = Column(String, nullable=False)  # Add user email
    verified = Column(Boolean, default=False)
    urgent = Column(Boolean, default=False)
    salary = Column(String, nullable=True)
    created_at = Column(String, default=lambda: datetime.now().isoformat())
    
    # New fields for required workers and hide/soft delete
    required_workers = Column(Integer, default=1)  # Number of workers needed
    hired_count = Column(Integer, default=0)  # Number of workers hired so far
    is_hidden = Column(Boolean, default=False)  # Soft delete - hide job by owner

    @property
    def is_verified(self):
        return self.verified
    
    @property
    def vacancies(self):
        """Calculate remaining vacancies"""
        return max(0, self.required_workers - self.hired_count)


class SavedJob(Base):
    __tablename__ = "saved_jobs"

    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String, nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    saved_at = Column(String, default=lambda: datetime.now().isoformat())
