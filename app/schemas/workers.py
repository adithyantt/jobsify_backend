from pydantic import BaseModel, ConfigDict
from typing import Optional

class WorkerCreate(BaseModel):
    name: str
    role: str
    phone: str
    experience: int
    location: str
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    user_email: str  # Add user email

    model_config = ConfigDict(from_attributes=True)

class WorkerResponse(WorkerCreate):
    id: int
    rating: float
    reviews: int
    is_available: bool
    is_verified: bool
