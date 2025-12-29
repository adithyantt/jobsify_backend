from pydantic import BaseModel, EmailStr

# ✅ For Registration
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str


# ✅ For Login
class UserLogin(BaseModel):
    email: EmailStr
    password: str
