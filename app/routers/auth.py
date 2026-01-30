from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.user import UserCreate, UserLogin
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Auth"])

# 🔐 PREDEFINED ADMIN EMAILS
ADMIN_EMAILS = [
    "admin@jobsify.com",
    "jobsify.admin@gmail.com"
]


# ✅ REGISTER
@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):

    # 🔍 Check if email already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # 🔐 Decide role automatically
    role = "admin" if user.email in ADMIN_EMAILS else "user"

    # 🆕 Create new user
    new_user = User(
        name=user.name,
        email=user.email,
        password=user.password,  # (plain for now, OK for project)
        role=role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User registered successfully",
        "role": role
    }


# ✅ LOGIN
@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):

    db_user = db.query(User).filter(User.email == user.email).first()

    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if db_user.password != user.password:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return {
        "message": "Login successful",
        "role": db_user.role,
        "email": db_user.email,
        "role": db_user.role
    }
