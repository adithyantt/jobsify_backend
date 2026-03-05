from pydantic import BaseModel, EmailStr, ConfigDict, field_validator
from typing import Optional
import re

# ✅ For Registration
class UserCreate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    name: Optional[str] = None  # Kept for backward compatibility
    email: EmailStr
    password: str
    phone: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one number')
        return v

    @field_validator('first_name', 'last_name', 'name')
    @classmethod
    def validate_names(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and len(v) > 0:
            # Remove extra whitespace
            v = ' '.join(v.split())
            if len(v) < 2:
                raise ValueError('Name must be at least 2 characters')
        return v

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and len(v) > 0:
            # Remove any spaces or dashes
            v = re.sub(r'[\s\-]', '', v)
            # Keep only digits
            v = ''.join(c for c in v if c.isdigit())
            # If more than 10 digits, take the last 10 (handles leading country code)
            if len(v) > 10:
                v = v[-10:]
            if not re.match(r'^\d{10}$', v):
                raise ValueError('Phone must be a valid 10-digit number')
        return v


# ✅ For Login
class UserLogin(BaseModel):
    email: EmailStr
    password: str

    model_config = ConfigDict(from_attributes=True)


# ✅ For Admin Users Response
class UserResponse(BaseModel):
    id: int
    first_name: Optional[str]
    last_name: Optional[str]
    name: Optional[str]
    email: str
    role: str
    phone: Optional[str]
    verified: bool
    email_verified: bool
    blocked: bool

    model_config = ConfigDict(from_attributes=True)
