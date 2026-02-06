from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.report import Report
from app.models.workers import Worker

router = APIRouter(
    prefix="/admin/reports",
    tags=["Admin Reports"]
)

# 🔹 GET ALL REPORTS
@router.get("/")
def get_all_reports(db: Session = Depends(get_db)):
    return db.query(Report).order_by(Report.id.desc()).all()


# 🔹 TAKE ACTION ON A REPORT
@router.post("/{report_id}/action")
def take_action_on_report(
    report_id: int,
    action: str,  # ignore | warn | ban
    db: Session = Depends(get_db)
):
    report = db.query(Report).filter(Report.id == report_id).first()

    if not report:
        return {"error": "Report not found"}

    if action not in ["ignored", "warned", "banned"]:
        return {"error": "Invalid action"}

    # update report status
    report.status = action

    # if banned → disable worker
    if action == "banned":
        worker = db.query(Worker).filter(
            Worker.id == report.worker_id
        ).first()
        if worker:
            worker.is_verified = False
            worker.is_available = False

    db.commit()

    return {
        "message": f"Report {action} successfully",
        "report_id": report_id,
    }
