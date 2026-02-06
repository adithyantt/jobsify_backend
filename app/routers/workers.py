from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.workers import Worker
from app.schemas.workers import WorkerCreate, WorkerResponse

router = APIRouter(prefix="/workers", tags=["Workers"])


# =====================================================
# 👤 USER SIDE – GET ONLY VERIFIED WORKERS
# =====================================================
@router.get("/", response_model=list[WorkerResponse])
def get_workers(db: Session = Depends(get_db)):
    return (
        db.query(Worker)
        .filter(Worker.is_verified == True)
        .all()
    )


# =====================================================
# 👤 USER SIDE – CREATE WORKER PROFILE
# (DEFAULT: is_verified = False)
# =====================================================
@router.post("/", response_model=WorkerResponse)
def create_worker(worker: WorkerCreate, db: Session = Depends(get_db)):
    new_worker = Worker(
        name=worker.name,
        role=worker.role,
        phone=worker.phone,
        experience=worker.experience,
        location=worker.location,
        latitude=worker.latitude,
        longitude=worker.longitude,
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

    return {
        "message": "Worker approved successfully",
        "worker_id": worker_id
    }
