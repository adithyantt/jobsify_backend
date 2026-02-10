from pydantic import BaseModel, ConfigDict
from typing import Optional

class JobCreate(BaseModel):
    title: str
    category: str
    description: str
    location: str
    phone: str
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    user_email: str  # Add user email
    urgent: Optional[bool] = False
    salary: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class JobResponse(JobCreate):
    id: int
    is_verified: bool
    verified: bool
    created_at: str
