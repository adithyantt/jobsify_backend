from pydantic import BaseModel, ConfigDict
from typing import Optional

class ReportCreate(BaseModel):
    worker_id: Optional[int] = None
    job_id: Optional[int] = None
    reporter_email: str
    reason: str
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class ReportResponse(ReportCreate):
    id: int
