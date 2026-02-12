from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional

# ✅ For Registration
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# ✅ For Login
class UserLogin(BaseModel):
    email: EmailStr
    password: str

    model_config = ConfigDict(from_attributes=True)


# ✅ For Admin Users Response
class UserResponse(BaseModel):
    id: int
    name: Optional[str]
    email: str
    role: str
    phone: Optional[str]
    verified: bool
    email_verified: bool
    blocked: bool

    model_config = ConfigDict(from_attributes=True)
