from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional
import re

class WorkerCreate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    name: Optional[str] = None
    role: str
    phone: str
    experience: int
    location: str
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    user_email: str
    availability_type: Optional[str] = "everyday"
    available_days: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

    @field_validator('first_name', 'last_name', 'name')
    @classmethod
    def validate_names(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and len(v) > 0:
            v = ' '.join(v.split())
            if len(v) < 2:
                raise ValueError('Name must be at least 2 characters')
            if len(v) > 50:
                raise ValueError('Name must not exceed 50 characters')
        return v

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        v = re.sub(r'[\s\-]', '', v)
        v = ''.join(c for c in v if c.isdigit())
        if len(v) > 10:
            v = v[-10:]
        if not re.match(r'^\d{10}$', v):
            raise ValueError('Phone must be a valid 10-digit number')
        return v

    @field_validator('experience')
    @classmethod
    def validate_experience(cls, v: int) -> int:
        if v < 0:
            raise ValueError('Experience cannot be negative')
        if v > 50:
            raise ValueError('Experience must not exceed 50 years')
        return v

    @field_validator('location')
    @classmethod
    def validate_location(cls, v: str) -> str:
        v = ' '.join(v.split())
        if len(v) < 2:
            raise ValueError('Location must be at least 2 characters long')
        if len(v) > 200:
            raise ValueError('Location must not exceed 200 characters')
        return v

    @field_validator('role')
    @classmethod
    def validate_role(cls, v: str) -> str:
        v = v.strip()
        v_lower = v.lower()
        role_map = {
            "plumbing": "Plumber",
            "painting": "Painter",
            "painter": "Painter",
            "cleaning": "Cleaner",
            "driver": "Driver",
            "electrician": "Electrician",
            "carpenter": "Carpenter"
        }
        if v_lower in role_map:
            return role_map[v_lower]
        valid_roles = ["Plumber", "Painter", "Driver", "Electrician", "Carpenter", "Cleaner"]
        if v not in valid_roles:
            raise ValueError(f'Role must be one of: {", ".join(valid_roles)}')
        return v


# Response model without validators
class WorkerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    name: Optional[str] = None
    role: str
    phone: str
    experience: int
    location: str
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    user_email: str
    availability_type: str = "everyday"
    available_days: Optional[str] = None
    rating: float = 0.0
    reviews: int = 0
    is_available: bool = True
    is_verified: bool = False
