from pydantic import BaseModel, ConfigDict, field_validator, Field
from typing import Optional
import re

class JobCreate(BaseModel):
    title: str
    category: str
    description: str
    location: str
    phone: str
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    user_email: str
    urgent: Optional[bool] = False
    salary: Optional[str] = None
    required_workers: Optional[int] = 1

    model_config = ConfigDict(from_attributes=True)

    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        v = ' '.join(v.split())
        if len(v) < 2:
            raise ValueError('Title must be at least 2 characters long')
        if len(v) > 100:
            raise ValueError('Title must not exceed 100 characters')
        return v

    @field_validator('description')
    @classmethod
    def validate_description(cls, v: str) -> str:
        v = ' '.join(v.split())
        if len(v) < 10:
            raise ValueError('Description must be at least 10 characters long')
        if len(v) > 2000:
            raise ValueError('Description must not exceed 2000 characters')
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

    @field_validator('required_workers')
    @classmethod
    def validate_required_workers(cls, v: Optional[int]) -> int:
        if v is not None and v < 1:
            raise ValueError('Required workers must be at least 1')
        if v is not None and v > 100:
            raise ValueError('Required workers must not exceed 100')
        return v if v is not None else 1

    @field_validator('category')
    @classmethod
    def validate_category(cls, v: str) -> str:
        v = v.strip()
        v_lower = v.lower()
        category_map = {
            "plumber": "Plumber",
            "plumbing": "Plumber",
            "painter": "Painter",
            "painting": "Painter",
            "driver": "Driver",
            "electrician": "Electrician",
            "carpenter": "Carpenter",
            "cleaner": "Cleaner",
            "cleaning": "Cleaner"
        }
        if v_lower in category_map:
            return category_map[v_lower]
        valid_categories = ["Plumber", "Painter", "Driver", "Electrician", "Carpenter", "Cleaner"]
        if v not in valid_categories:
            raise ValueError(f'Category must be one of: {", ".join(valid_categories)}')
        return v


# Response model without validators (for returning data from DB)
class JobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    title: str
    category: str
    description: str
    location: str
    phone: str
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    user_email: str
    urgent: bool = False
    salary: Optional[str] = None
    required_workers: int = 1
    is_verified: bool = False
    verified: bool = False
    created_at: str
    hired_count: int = 0
    is_hidden: bool = False
    vacancies: int = 1


class SavedJobCreate(BaseModel):
    user_email: str
    job_id: int
    model_config = ConfigDict(from_attributes=True)


class SavedJobResponse(BaseModel):
    id: int
    user_email: str
    job_id: int
    saved_at: str
    model_config = ConfigDict(from_attributes=True)
