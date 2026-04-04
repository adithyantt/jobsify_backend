from sqlalchemy import Column, Integer, String, Boolean, Float, Index
from app.database import Base


class Worker(Base):
    __tablename__ = "workers"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    name = Column(String)
    role = Column(String, index=True)
    phone = Column(String)
    experience = Column(Integer, index=True)
    location = Column(String, index=True)
    latitude = Column(String, nullable=True)
    longitude = Column(String, nullable=True)
    user_email = Column(String, nullable=False, index=True)
    is_verified = Column(Boolean, default=False, index=True)
    availability_type = Column(String, default="everyday", index=True)
    available_days = Column(String, nullable=True)
    is_available = Column(Boolean, default=True, index=True)
    rating = Column(Float, default=0, index=True)
    reviews = Column(Integer, default=0)

    __table_args__ = (
        Index('idx_workers_verified_available', 'is_verified', 'is_available'),
        Index('idx_workers_role_verified', 'role', 'is_verified'),
        Index('idx_workers_location_verified', 'location', 'is_verified'),
    )
