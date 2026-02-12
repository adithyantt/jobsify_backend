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

    @property
    def is_verified(self):
        return self.verified


class SavedJob(Base):
    __tablename__ = "saved_jobs"

    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String, nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    saved_at = Column(String, default=lambda: datetime.now().isoformat())
