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
