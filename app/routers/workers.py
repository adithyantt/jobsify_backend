from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.workers import Worker
<<<<<<< HEAD
from app.models.report import Report
from app.models.notification import Notification
from app.schemas.workers import WorkerCreate, WorkerResponse
from app.schemas.report import ReportCreate, ReportResponse
=======
from app.schemas.workers import WorkerCreate, WorkerOut
>>>>>>> origin/main

router = APIRouter(prefix="/workers", tags=["Workers"])


<<<<<<< HEAD
# =====================================================
# 👤 USER SIDE – GET ONLY VERIFIED WORKERS
# =====================================================
@router.get("", response_model=list[WorkerResponse])
def get_workers(db: Session = Depends(get_db)):
    return (
        db.query(Worker)
        .filter(Worker.is_verified == True)
=======
# 🔹 GET VERIFIED & AVAILABLE WORKERS
@router.get("", response_model=list[WorkerOut])
def get_workers(db: Session = Depends(get_db)):
    return (
        db.query(Worker)
        .filter(
            Worker.is_verified == True,
            Worker.is_available == True
        )
>>>>>>> origin/main
        .all()
    )


<<<<<<< HEAD
# =====================================================
# 👤 USER SIDE – GET MY WORKERS (BY EMAIL)
# =====================================================
@router.get("/my", response_model=list[WorkerResponse])
def get_my_workers(email: str, db: Session = Depends(get_db)):
    return (
        db.query(Worker)
        .filter(Worker.user_email == email)
        .all()
    )


# =====================================================
# 👤 USER SIDE – CREATE WORKER PROFILE
# (DEFAULT: is_verified = False)
# =====================================================
@router.post("", response_model=WorkerResponse)
def create_worker(worker: WorkerCreate, db: Session = Depends(get_db)):
    new_worker = Worker(
        name=worker.name,
        role=worker.role,
        phone=worker.phone,
        experience=worker.experience,
        location=worker.location,
        latitude=worker.latitude,
        longitude=worker.longitude,
        user_email=worker.user_email,  # Add user email
        is_verified=False,     # 🔒 Admin must approve
        is_available=True
    )

    db.add(new_worker)
    db.commit()
    db.refresh(new_worker)

    return new_worker


# =====================================================
# 🛡️ ADMIN SIDE – GET PENDING WORKERS
# =====================================================
@router.get("/admin/pending", response_model=list[WorkerResponse])
def get_pending_workers(db: Session = Depends(get_db)):
    return (
        db.query(Worker)
        .filter(Worker.is_verified == False)
        .all()
    )


# =====================================================
# 🛡️ ADMIN SIDE – APPROVE WORKER
# =====================================================
@router.put("/admin/approve/{worker_id}")
def approve_worker(worker_id: int, db: Session = Depends(get_db)):
    worker = db.query(Worker).filter(Worker.id == worker_id).first()

    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")

    worker.is_verified = True
    db.commit()

    # Create notification for the user
    notification = Notification(
        user_email=worker.user_email,
        title="Worker Approved",
        message=f"Your worker profile '{worker.name}' has been approved and is now live."
    )
    db.add(notification)
    db.commit()

    return {
        "message": "Worker approved successfully",
        "worker_id": worker_id
    }


# =====================================================
# 🛡️ ADMIN SIDE – REJECT WORKER
# =====================================================
@router.put("/admin/reject/{worker_id}")
def reject_worker(worker_id: int, db: Session = Depends(get_db)):
    worker = db.query(Worker).filter(Worker.id == worker_id).first()

    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")

    db.delete(worker)
    db.commit()

    return {
        "message": "Worker rejected and deleted successfully",
        "worker_id": worker_id
    }


# =====================================================
# 👤 USER SIDE – UPDATE WORKER
# =====================================================
@router.put("/{worker_id}", response_model=WorkerResponse)
def update_worker(worker_id: int, worker: WorkerCreate, email: str = Query(...), db: Session = Depends(get_db)):
    existing_worker = db.query(Worker).filter(Worker.id == worker_id, Worker.user_email == email).first()

    if not existing_worker:
        raise HTTPException(status_code=404, detail="Worker not found or not owned by user")

    existing_worker.name = worker.name
    existing_worker.role = worker.role
    existing_worker.phone = worker.phone
    existing_worker.experience = worker.experience
    existing_worker.location = worker.location
    existing_worker.latitude = worker.latitude
    existing_worker.longitude = worker.longitude

    db.commit()
    db.refresh(existing_worker)

    return existing_worker


# =====================================================
# 👤 USER SIDE – DELETE WORKER
# =====================================================
@router.delete("/{worker_id}")
def delete_worker(worker_id: int, email: str = Query(...), db: Session = Depends(get_db)):
    worker = db.query(Worker).filter(Worker.id == worker_id, Worker.user_email == email).first()

    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found or not owned by user")

    db.delete(worker)
    db.commit()

    return {
        "message": "Worker deleted successfully",
        "worker_id": worker_id
    }


# =====================================================
# 👤 USER SIDE – REPORT WORKER
# =====================================================
@router.post("/report", response_model=ReportResponse)
def report_worker(report: ReportCreate, db: Session = Depends(get_db)):
    # Check if worker exists
    if report.worker_id is None:
        raise HTTPException(status_code=400, detail="worker_id is required for worker reports")

    worker = db.query(Worker).filter(Worker.id == report.worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")

    new_report = Report(
        worker_id=report.worker_id,
        reporter_email=report.reporter_email,
        reason=report.reason,
        description=report.description,
        status="pending"
    )

    db.add(new_report)
    db.commit()
    db.refresh(new_report)

    return new_report
=======
# 🔹 CREATE WORKER (availability set by user)
@router.post("", status_code=201)
def create_worker(data: WorkerCreate, db: Session = Depends(get_db)):
    worker = Worker(**data.dict())
    db.add(worker)
    db.commit()
    db.refresh(worker)
    return {"success": True}
>>>>>>> origin/main
