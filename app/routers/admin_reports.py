from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.report import Report
from app.models.workers import Worker

router = APIRouter(prefix="/admin/reports", tags=["Admin Reports"])


# 🔹 ADMIN ACTION ON REPORT
@router.put("/{report_id}/action")
def take_action_on_report(
    report_id: int,
    action: str,
    db: Session = Depends(get_db)
):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    if action == "ignore":
        report.status = "ignored"

    elif action == "resolve":
        report.status = "resolved"

    elif action == "ban":
        worker = db.query(Worker).filter(Worker.id == report.worker_id).first()
        if worker:
            worker.is_available = False
        report.status = "resolved"

    else:
        raise HTTPException(status_code=400, detail="Invalid action")

    db.commit()
    return {
        "message": f"Report {action}d successfully"
    }
