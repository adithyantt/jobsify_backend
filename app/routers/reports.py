from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.report import Report
from app.schemas.report import ReportCreate, ReportOut

router = APIRouter(prefix="/reports", tags=["Reports"])


# 🔹 USER CREATES REPORT
@router.post("", response_model=ReportOut, status_code=201)
def create_report(data: ReportCreate, db: Session = Depends(get_db)):
    report = Report(
        worker_id=data.worker_id,
        reason=data.reason,
        description=data.description
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report
