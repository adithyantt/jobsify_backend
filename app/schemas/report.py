from pydantic import BaseModel

class ReportCreate(BaseModel):
    worker_id: int
    reason: str
    description: str | None = None

class ReportResponse(ReportCreate):
    id: int

    class Config:
        from_attributes = True
