from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import bcrypt
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from datetime import datetime, timedelta

from app.database import get_db
from app.schemas.user import UserCreate, UserLogin
from app.models.user import User

# JWT Configuration
JWT_SECRET = "your-secret-key-change-in-production"  # Change this in production!
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24


security = HTTPBearer()

router = APIRouter(prefix="/auth", tags=["Auth"])

# Temporary OTP storage (use Redis in production)
otp_storage = {}

# 🔐 PREDEFINED ADMIN EMAILS (DEV ONLY)
ADMIN_EMAILS = [
    "admin@jobsify.com",
    "jobsify.admin@gmail.com",
    "superadmin@jobsify.com"
]

# 📧 EMAIL CONFIGURATION (Replace with your credentials)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "adithyancoding@gmail.com"  # Replace with your Gmail
SENDER_PASSWORD = "famn yqnn rjlz lhyl"  # Replace with Gmail App Password

def send_otp_email(recipient_email: str, otp: str):
    """Send OTP via email using Gmail SMTP."""
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = recipient_email
        msg['Subject'] = "Your OTP for Jobsify Email Verification"

        body = f"""
        Hello,

        Your OTP for email verification on Jobsify is: {otp}

        This OTP is valid for a short time. Please do not share it with anyone.

        If you did not request this, please ignore this email.

        Best regards,
        Jobsify Team
        """
        msg.attach(MIMEText(body, 'plain'))

        # Connect to SMTP server
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        text = msg.as_string()
        server.sendmail(SENDER_EMAIL, recipient_email, text)
        server.quit()

        print(f"OTP email sent to {recipient_email}")
        return True
    except Exception as e:
        print(f"Failed to send OTP email to {recipient_email}: {e}")
        return False


# ================= REGISTER =================
@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):

    # 🔍 Check if email already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        if existing_user.email_verified:
            raise HTTPException(status_code=400, detail="Email already registered")
        else:
            # Resend OTP for unverified user
            otp = str(random.randint(100000, 999999))
            otp_storage[existing_user.email] = otp
            send_otp_email(existing_user.email, otp)
            return {
                "message": "OTP resent. Please verify your email.",
                "user_id": existing_user.id,
                "role": existing_user.role
            }

    # Validate password strength
    if len(user.password) < 8 or not any(c.isupper() for c in user.password) or not any(c.islower() for c in user.password) or not any(c.isdigit() for c in user.password):
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters long and include uppercase, lowercase, and numeric characters.")

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
        role=role,
        phone=user.phone,
        verified=False
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Generate and send OTP
    otp = str(random.randint(100000, 999999))
    otp_storage[new_user.email] = otp
    send_otp_email(new_user.email, otp)

    return {
        "message": "User registered successfully. Please verify your email with the OTP sent.",
        "user_id": new_user.id,
        "role": role
    }


# ✅ VERIFY OTP
@router.post("/verify-otp")
def verify_otp(data: dict, db: Session = Depends(get_db)):
    user_id = data.get("user_id")
    otp = data.get("otp")

    # Get user by id
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    if db_user.email not in otp_storage:
        raise HTTPException(status_code=400, detail="OTP not found or expired")

    if otp_storage[db_user.email] != otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    # Mark user as email verified
    db_user.email_verified = True
    db.commit()

    # Remove OTP from storage
    del otp_storage[db_user.email]

    # Create JWT access token for the newly verified user
    access_token = create_access_token(data={"sub": db_user.email})

    return {
        "message": "Email verified successfully",
        "email": db_user.email,
        "role": db_user.role,
        "name": db_user.name,
        "access_token": access_token,
        "token_type": "bearer"
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

    # Skip OTP verification for admins
    if not db_user.email_verified and db_user.role != "admin":
        # Resend OTP for unverified user
        otp = str(random.randint(100000, 999999))
        otp_storage[db_user.email] = otp
        send_otp_email(db_user.email, otp)
        return {
            "unverified": True,
            "user_id": db_user.id,
            "name": db_user.name,
            "message": "Account not verified. OTP sent to your email. Please verify your email."
        }

    # Create JWT access token
    access_token = create_access_token(data={"sub": db_user.email})

    return {
        "message": "Login successful",
        "id": db_user.id,
        "name": db_user.name,
        "email": db_user.email,
        "role": db_user.role,
        "access_token": access_token,
        "token_type": "bearer"
    }


def create_access_token(data: dict):
    """Create a JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    """Verify and decode a JWT token."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")


# 🔐 GET CURRENT ADMIN (Dependency for protected routes)
def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    print(f"DEBUG: Authorization header received: {credentials}")
    print(f"DEBUG: Token: {credentials.credentials[:50]}..." if len(credentials.credentials) > 50 else f"DEBUG: Token: {credentials.credentials}")
    token = credentials.credentials
    
    # Check for null/empty/invalid token before attempting JWT verification
    if not token or token == "null" or token == "undefined" or token.strip() == "":
        print(f"DEBUG: Invalid token value received: '{token}'")
        raise HTTPException(status_code=401, detail="Authentication required. Please login.")

    try:
        payload = verify_token(token)
        print(f"DEBUG: Token payload: {payload}")
        email = payload.get("sub")
        print(f"DEBUG: Email from token: {email}")
        if not email:


            raise HTTPException(status_code=401, detail="Invalid token payload")

        print(f"DEBUG: ADMIN_EMAILS list: {ADMIN_EMAILS}")
        print(f"DEBUG: Is {email} in ADMIN_EMAILS? {email in ADMIN_EMAILS}")
        
        # Check if user is in predefined admin emails list
        if email in ADMIN_EMAILS:
            # Get or create admin user
            user = db.query(User).filter(User.email == email).first()
            print(f"DEBUG: User query result: {user}")
            if user:


                # Update role to admin if not already set
                if user.role != "admin":
                    user.role = "admin"
                    db.commit()
                return user
            else:
                # Admin email not found in DB - this shouldn't happen for predefined admins
                pass

        # Fallback: check database for role="admin"
        user = db.query(User).filter(User.email == email, User.role == "admin").first()
        print(f"DEBUG: Fallback query result: {user}")
        if not user:
            print(f"DEBUG: No admin user found, raising 401")
            raise HTTPException(status_code=401, detail="Invalid token or not admin")
        print(f"DEBUG: Admin user found, returning user")
        return user
    except HTTPException as he:
        print(f"DEBUG: HTTPException raised: {he.detail}")
        raise
    except Exception as e:
        print(f"DEBUG: Exception in get_current_admin: {str(e)}")
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")


# 🔐 GET CURRENT USER (Dependency for any authenticated user)
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """Verify token and return current user (any role)."""
    token = credentials.credentials
    
    # Check for null/empty/invalid token before attempting JWT verification
    if not token or token == "null" or token == "undefined" or token.strip() == "":
        print(f"DEBUG: Invalid token value received in get_current_user: '{token}'")
        raise HTTPException(status_code=401, detail="Authentication required. Please login.")
    
    try:

        payload = verify_token(token)
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")


# ================= SESSION MANAGEMENT =================

# 📋 GET CURRENT USER INFO (For frontend session check)
@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    """
    Returns current user info if token is valid.
    Frontend calls this on app load to check session and get role for routing.
    """
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "role": current_user.role,
        "email_verified": current_user.email_verified,
        "verified": current_user.verified
    }


# 🔄 REFRESH TOKEN (Extend session)
@router.post("/refresh")
def refresh_token(current_user: User = Depends(get_current_user)):
    """
    Refresh access token to extend session expiration.
    Call this when user is active to prevent automatic logout.
    """
    # Create new token with fresh expiration
    new_token = create_access_token(data={"sub": current_user.email})
    
    return {
        "message": "Token refreshed successfully",
        "access_token": new_token,
        "token_type": "bearer"
    }


# 🚪 LOGOUT (Client-side token removal)
@router.post("/logout")
def logout():
    """
    Logout endpoint. Frontend should remove token from storage.
    This is mainly for logging purposes.
    """
    return {
        "message": "Logout successful. Please remove token from client storage."
    }
