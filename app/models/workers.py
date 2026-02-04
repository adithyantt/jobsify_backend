from sqlalchemy import Column, Integer, String, Boolean, Float
from app.database import Base

class Worker(Base):
    __tablename__ = "workers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    role = Column(String)
    phone = Column(String)
    experience = Column(Integer)
    location = Column(String)
    latitude = Column(String, nullable=True)
    longitude = Column(String, nullable=True)

    is_verified = Column(Boolean, default=False)
    is_available = Column(Boolean, default=True)
    rating = Column(Float, default=4.0)
    reviews = Column(Integer, default=0)
