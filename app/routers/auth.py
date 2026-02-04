from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import bcrypt

from app.database import get_db
from app.schemas.user import UserCreate, UserLogin
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Auth"])

# 🔐 PREDEFINED ADMIN EMAILS (DEV ONLY)
ADMIN_EMAILS = [
    "admin@jobsify.com",
    "jobsify.admin@gmail.com"
]


# ================= REGISTER =================
@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):

    # 🔍 Check if email already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # 🔐 Decide role
    role = "admin" if user.email in ADMIN_EMAILS else "seeker"

    # 🔐 Hash password
    hashed_password = bcrypt.hashpw(
        user.password.encode(),
        bcrypt.gensalt()
    ).decode()

    # 🆕 Create user
    new_user = User(
        name=user.name,
        email=user.email,
        password=hashed_password,
        role=role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User registered successfully",
        "role": role
    }


# ================= LOGIN =================
@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):

    db_user = db.query(User).filter(User.email == user.email).first()

    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not bcrypt.checkpw(
        user.password.encode(),
        db_user.password.encode()
    ):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return {
        "message": "Login successful",
        "id": db_user.id,
        "name": db_user.name,
        "email": db_user.email,
        "role": db_user.role
    }
