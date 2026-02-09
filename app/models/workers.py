from sqlalchemy import Column, Integer, String, Float, Boolean
from app.database import Base

class Worker(Base):
    __tablename__ = "workers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    role = Column(String, nullable=False)
    phone = Column(String, nullable=False)

    experience = Column(Integer, nullable=False)  # years
    rating = Column(Float, default=0.0)
    reviews = Column(Integer, default=0)

    location = Column(String, nullable=False)
    latitude = Column(String, nullable=True)
    longitude = Column(String, nullable=True)

    user_email = Column(String, nullable=False)  # Add user email
    is_available = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
