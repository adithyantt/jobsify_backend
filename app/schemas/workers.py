from pydantic import BaseModel

class WorkerCreate(BaseModel):
    name: str
    role: str
    phone: str
    experience: int
    location: str
    latitude: str | None = None
    longitude: str | None = None

class WorkerResponse(WorkerCreate):
    id: int
    rating: float
    reviews: int
    is_available: bool
    is_verified: bool

    class Config:
        from_attributes = True
