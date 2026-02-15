from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.models.report import Report
from app.models.workers import Worker
from app.models.notification import Notification
from app.models.user import User
from app.schemas.report import ReportResponse
from app.routers.auth import get_current_admin

router = APIRouter(
    prefix="/admin/reports",
    tags=["Admin Reports"]
)


class ReportActionRequest(BaseModel):
    action: str  # ignore | warn | ban


@router.get("/")
def get_all_reports(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    return db.query(Report).order_by(Report.id.desc()).all()


@router.get("/pending")
def get_pending_reports(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    return db.query(Report).filter(Report.status == "pending").order_by(Report.id.desc()).all()


@router.put("/{report_id}/action")
def take_action_on_report(
    report_id: int,
    action_data: Optional[ReportActionRequest] = None,
    action: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    # Accept both body and query param to avoid frontend/backend mismatch.
    resolved_action = (action_data.action if action_data else action)

    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    action_mapping = {
        "ignore": "ignored",
        "warn": "warned",
        "ban": "banned",
    }

    if not resolved_action or resolved_action not in action_mapping:
        raise HTTPException(status_code=400, detail="Invalid action")

    status = action_mapping[resolved_action]
    report.status = status

    if status == "banned" and report.worker_id is not None:
        worker = db.query(Worker).filter(Worker.id == report.worker_id).first()
        if worker:
            worker.is_verified = False
            worker.is_available = False

    target = f"worker ID {report.worker_id}" if report.worker_id is not None else f"job ID {report.job_id}"
    
    # Determine type and reference_id based on report target
    notification_type = "worker" if report.worker_id is not None else "job"
    reference_id = report.worker_id if report.worker_id is not None else report.job_id

    notification = Notification(
        user_email=report.reporter_email,
        title="Report Action Taken",
        message=f"Your report on {target} has been {status}.",
        type=notification_type,
        reference_id=reference_id
    )
    db.add(notification)

    db.commit()

    return {
        "message": f"Report {status} successfully",
        "report_id": report_id,
    }
