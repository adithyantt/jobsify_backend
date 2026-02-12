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
    user_email = Column(String, nullable=False)  # Add user email
    is_verified = Column(Boolean, default=False)
    # Availability fields
    availability_type = Column(String, default="everyday")  # everyday | selected_days | not_available
    available_days = Column(String, nullable=True)  # Comma-separated days: "Mon,Tue,Wed"
    is_available = Column(Boolean, default=True)
    rating = Column(Float, default=4.0)
    reviews = Column(Integer, default=0)
