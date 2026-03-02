from sqlalchemy import Column, Integer, String, Boolean
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=True)  # First name for atomicity
    last_name = Column(String, nullable=True)   # Last name for atomicity
    name = Column(String, nullable=True)         # Kept for backward compatibility
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)  # hashed password only
    role = Column(
        String,
        nullable=False,
        default="seeker"  # seeker / provider / admin
    )
    phone = Column(String, nullable=True)  # For future profile verification
    verified = Column(Boolean, default=False)  # For phone verification (future use)
    email_verified = Column(Boolean, default=False)  # For email verification
    blocked = Column(Boolean, default=False)  # For blocking users
