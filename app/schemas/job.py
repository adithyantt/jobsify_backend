from pydantic import BaseModel

class JobCreate(BaseModel):
    title: str
    category: str
    description: str
    location: str
    phone: str
    latitude: str | None = None
    longitude: str | None = None
    
class JobResponse(JobCreate):
    id: int
    is_verified: bool

    class Config:
        from_attributes = True
