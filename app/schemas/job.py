from pydantic import BaseModel
from typing import Optional

class JobCreate(BaseModel):
    title: str
    category: str
    description: Optional[str] = None
    location: str

class JobResponse(JobCreate):
    id: int

    class Config:
        orm_mode = True
