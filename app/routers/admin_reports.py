from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.models.report import Report
from app.models.workers import Worker
from app.models.notification import Notification
from app.models.user import User
from app.routers.auth import get_current_admin

router = APIRouter(
    prefix="/admin/reports",
    tags=["Admin Reports"]
)

# Request body model for report action
class ReportActionRequest(BaseModel):
    action: str  # ignore | warn | ban


# 🔹 GET ALL REPORTS
@router.get("/")
def get_all_reports(db: Session = Depends(get_db)):
    return db.query(Report).order_by(Report.id.desc()).all()

# 🔹 GET PENDING REPORTS
@router.get("/pending")
def get_pending_reports(db: Session = Depends(get_db)):
    return db.query(Report).filter(Report.status == "pending").order_by(Report.id.desc()).all()

# 🔹 TAKE ACTION ON A REPORT
@router.put("/{report_id}/action")
def take_action_on_report(
    report_id: int,
    action_data: ReportActionRequest,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    action = action_data.action

    report = db.query(Report).filter(Report.id == report_id).first()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    # Map frontend actions to backend statuses
    action_mapping = {
        "ignore": "ignored",
        "warn": "warned",
        "ban": "banned"
    }

    if action not in action_mapping:
        raise HTTPException(status_code=400, detail="Invalid action")

    status = action_mapping[action]

    # update report status
    report.status = status

    # if banned → disable worker
    if status == "banned":
        worker = db.query(Worker).filter(
            Worker.id == report.worker_id
        ).first()
        if worker:
            worker.is_verified = False
            worker.is_available = False

    # Create notification for the reporter
    notification = Notification(
        user_email=report.reporter_email,
        title="Report Action Taken",
        message=f"Your report on worker ID {report.worker_id} has been {status}."
    )
    db.add(notification)

    db.commit()

    return {
        "message": f"Report {status} successfully",
        "report_id": report_id
    }
