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
    availability_type: Optional[str] = "everyday"  # everyday | selected_days | not_available
    available_days: Optional[str] = None  # Comma-separated: "Mon,Tue,Wed"

    model_config = ConfigDict(from_attributes=True)

class WorkerResponse(WorkerCreate):
    id: int
    rating: float
    reviews: int
    is_available: bool
    is_verified: bool
