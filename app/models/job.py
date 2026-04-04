from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Index
from datetime import datetime
from app.database import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    category = Column(String, nullable=False, index=True)
    description = Column(String, nullable=False)
    location = Column(String, nullable=False, index=True)
    phone = Column(String, nullable=False)
    latitude = Column(String, nullable=True)
    longitude = Column(String, nullable=True)
    user_email = Column(String, nullable=False, index=True)
    verified = Column(Boolean, default=False, index=True)
    urgent = Column(Boolean, default=False)
    salary = Column(String, nullable=True)
    created_at = Column(String, default=lambda: datetime.now().isoformat(), index=True)
    
    required_workers = Column(Integer, default=1)
    hired_count = Column(Integer, default=0)
    is_hidden = Column(Boolean, default=False, index=True)

    @property
    def is_verified(self):
        return self.verified
    
    @property
    def vacancies(self):
        return max(0, self.required_workers - self.hired_count)

    __table_args__ = (
        Index('idx_jobs_verified_hidden', 'verified', 'is_hidden'),
        Index('idx_jobs_user_verified', 'user_email', 'verified'),
        Index('idx_jobs_category_verified', 'category', 'verified'),
    )


class SavedJob(Base):
    __tablename__ = "saved_jobs"

    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String, nullable=False, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False, index=True)
    saved_at = Column(String, default=lambda: datetime.now().isoformat())
    
    __table_args__ = (
        Index('idx_saved_jobs_user_job', 'user_email', 'job_id', unique=True),
    )
