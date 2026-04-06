from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import bcrypt
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from datetime import datetime, timedelta, timezone

from app.database import get_db
from app.schemas.user import UserCreate, UserLogin
from app.models.user import User
from app.middleware.rate_limiter import check_login_rate_limit, check_register_rate_limit, check_otp_rate_limit

JWT_SECRET = "your-secret-key-change-in-production"
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24
OTP_EXPIRATION_MINUTES = 5
OTP_PURPOSE_VERIFY_EMAIL = "verify-email"
OTP_PURPOSE_RESET_PASSWORD = "reset-password"

security = HTTPBearer()
router = APIRouter(prefix="/auth", tags=["Auth"])
otp_storage = {}

ADMIN_EMAILS = [
    "admin@jobsify.com",
    "jobsify.admin@gmail.com",
    "superadmin@jobsify.com"
]

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "adithyancoding@gmail.com"
SENDER_PASSWORD = "famn yqnn rjlz lhyl"


def send_otp_email(recipient_email: str, otp: str):
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = recipient_email
        msg['Subject'] = "Your OTP for Jobsify Email Verification"

        body = f"""
        Hello,

        Your OTP for Jobsify is: {otp}

        This OTP is valid for 5 minutes. Please do not share it with anyone.

        If you did not request this, please ignore this email.

        Best regards,
        Jobsify Team
        """
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, recipient_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Failed to send OTP email to {recipient_email}: {e}")
        return False


def validate_password_strength(password: str):
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters long")
    if not any(c.isupper() for c in password):
        raise HTTPException(status_code=400, detail="Password must contain at least one uppercase letter")
    if not any(c.islower() for c in password):
        raise HTTPException(status_code=400, detail="Password must contain at least one lowercase letter")
    if not any(c.isdigit() for c in password):
        raise HTTPException(status_code=400, detail="Password must contain at least one number")
    if all(c.isalnum() for c in password):
        raise HTTPException(status_code=400, detail="Password must contain at least one special character")


def _create_otp_record(purpose: str) -> dict:
    otp = str(random.randint(100000, 999999))
    return {
        "code": otp,
        "purpose": purpose,
        "expires_at": datetime.now(timezone.utc) + timedelta(minutes=OTP_EXPIRATION_MINUTES),
    }


def _store_otp(email: str, purpose: str) -> str:
    record = _create_otp_record(purpose)
    otp_storage[email] = record
    send_otp_email(email, record["code"])
    return record["code"]


def _get_valid_otp_record(email: str, purpose: str | None = None):
    record = otp_storage.get(email)
    if not record:
        return None

    expires_at = record.get("expires_at")
    if not expires_at or datetime.now(timezone.utc) > expires_at:
        otp_storage.pop(email, None)
        return None

    if purpose and record.get("purpose") != purpose:
        return None

    return record


@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    check_register_rate_limit(user.email)

    normalized_email = user.email.lower()
    existing_user = db.query(User).filter(User.email == normalized_email).first()
    if existing_user:
        if existing_user.email_verified:
            raise HTTPException(status_code=400, detail="Email already registered")

        _store_otp(existing_user.email, OTP_PURPOSE_VERIFY_EMAIL)
        return {
            "message": "OTP resent. Please verify your email.",
            "user_id": existing_user.id,
            "role": existing_user.role,
            "otp_expires_in_seconds": OTP_EXPIRATION_MINUTES * 60,
        }

    validate_password_strength(user.password)
    role = "admin" if normalized_email in ADMIN_EMAILS else "user"
    hashed_password = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt()).decode()

    new_user = User(
        first_name=(user.first_name or "").strip() or None,
        last_name=(user.last_name or "").strip() or None,
        email=normalized_email,
        password=hashed_password,
        role=role,
        phone=user.phone,
        email_verified=False,
        blocked=False,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    _store_otp(new_user.email, OTP_PURPOSE_VERIFY_EMAIL)

    return {
        "message": "User registered successfully. Please verify your email with the OTP sent.",
        "user_id": new_user.id,
        "role": role,
        "otp_expires_in_seconds": OTP_EXPIRATION_MINUTES * 60,
    }


@router.post("/verify-otp")
def verify_otp(data: dict, db: Session = Depends(get_db)):
    user_id = data.get("user_id")
    otp = (data.get("otp") or "").strip()

    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    record = _get_valid_otp_record(db_user.email, OTP_PURPOSE_VERIFY_EMAIL)
    if not record:
        raise HTTPException(status_code=400, detail="OTP not found or expired")

    if record["code"] != otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    db_user.email_verified = True
    db.commit()
    otp_storage.pop(db_user.email, None)

    access_token = create_access_token(data={"sub": db_user.email})
    return {
        "message": "Email verified successfully",
        "email": db_user.email,
        "role": db_user.role,
        "first_name": db_user.first_name,
        "last_name": db_user.last_name,
        "phone": db_user.phone,
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.post("/forgot-password/request")
def request_password_reset(data: dict, db: Session = Depends(get_db)):
    email = (data.get("email") or "").strip().lower()
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")

    check_otp_rate_limit(email)
    db_user = db.query(User).filter(User.email == email).first()
    if db_user and db_user.email_verified:
        _store_otp(db_user.email, OTP_PURPOSE_RESET_PASSWORD)

    return {
        "message": "If the account exists, a reset OTP has been sent. The OTP is valid for 5 minutes.",
        "otp_expires_in_seconds": OTP_EXPIRATION_MINUTES * 60,
    }


@router.post("/forgot-password/reset")
def reset_password(data: dict, db: Session = Depends(get_db)):
    email = (data.get("email") or "").strip().lower()
    otp = (data.get("otp") or "").strip()
    new_password = data.get("new_password") or ""

    if not email or not otp or not new_password:
        raise HTTPException(status_code=400, detail="Email, OTP, and new password are required")

    validate_password_strength(new_password)
    db_user = db.query(User).filter(User.email == email).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    record = _get_valid_otp_record(email, OTP_PURPOSE_RESET_PASSWORD)
    if not record:
        raise HTTPException(status_code=400, detail="OTP not found or expired")

    if record["code"] != otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    db_user.password = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
    db.commit()
    otp_storage.pop(email, None)
    return {"message": "Password reset successful"}


@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    check_login_rate_limit(user.email)

    normalized_email = user.email.lower()
    db_user = db.query(User).filter(User.email == normalized_email).first()
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if db_user.blocked:
        raise HTTPException(status_code=403, detail="Account blocked. Please contact support.")

    if not bcrypt.checkpw(user.password.encode(), db_user.password.encode()):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not db_user.email_verified and db_user.role != "admin":
        _store_otp(db_user.email, OTP_PURPOSE_VERIFY_EMAIL)
        return {
            "unverified": True,
            "user_id": db_user.id,
            "first_name": db_user.first_name,
            "last_name": db_user.last_name,
            "message": "Account not verified. OTP sent to your email. Please verify your email.",
            "otp_expires_in_seconds": OTP_EXPIRATION_MINUTES * 60,
        }

    access_token = create_access_token(data={"sub": db_user.email})
    return {
        "message": "Login successful",
        "id": db_user.id,
        "first_name": db_user.first_name,
        "last_name": db_user.last_name,
        "email": db_user.email,
        "role": db_user.role,
        "phone": db_user.phone,
        "access_token": access_token,
        "token_type": "bearer",
    }


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_token(token: str):
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")


def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    if not token or token == "null" or token == "undefined" or token.strip() == "":
        raise HTTPException(status_code=401, detail="Authentication required. Please login.")

    try:
        payload = verify_token(token)
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        if email in ADMIN_EMAILS:
            user = db.query(User).filter(User.email == email).first()
            if user:
                if user.role != "admin":
                    user.role = "admin"
                    db.commit()
                return user

        user = db.query(User).filter(User.email == email, User.role == "admin").first()
        if not user:
            raise HTTPException(status_code=401, detail="Invalid token or not admin")
        return user
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(exc)}")


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    if not token or token == "null" or token == "undefined" or token.strip() == "":
        raise HTTPException(status_code=401, detail="Authentication required. Please login.")

    try:
        payload = verify_token(token)
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        if user.blocked:
            raise HTTPException(status_code=403, detail="Account blocked. Please contact support.")
        return user
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(exc)}")


@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "email": current_user.email,
        "role": current_user.role,
        "phone": current_user.phone,
        "email_verified": current_user.email_verified,
        "blocked": current_user.blocked,
    }


@router.post("/refresh")
def refresh_token(current_user: User = Depends(get_current_user)):
    new_token = create_access_token(data={"sub": current_user.email})
    return {
        "message": "Token refreshed successfully",
        "access_token": new_token,
        "token_type": "bearer",
    }


@router.post("/logout")
def logout():
    return {"message": "Logout successful. Please remove token from client storage."}
