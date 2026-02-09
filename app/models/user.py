from sqlalchemy import Column, Integer, String, Boolean
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    role = Column(String) #seeker / provider / admin
    phone = Column(String, nullable=True)  # For future profile verification
    verified = Column(Boolean, default=False)  # For phone verification (future use)
    email_verified = Column(Boolean, default=False)  # For email verification
    blocked = Column(Boolean, default=False)  # For blocking users
    