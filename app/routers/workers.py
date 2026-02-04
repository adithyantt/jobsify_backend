from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.workers import Worker
from app.schemas.workers import WorkerCreate, WorkerOut

router = APIRouter(prefix="/workers", tags=["Workers"])


# 🔹 GET VERIFIED & AVAILABLE WORKERS
@router.get("", response_model=list[WorkerOut])
def get_workers(db: Session = Depends(get_db)):
    return (
        db.query(Worker)
        .filter(
            Worker.is_verified == True,
            Worker.is_available == True
        )
        .all()
    )


# 🔹 CREATE WORKER (availability set by user)
@router.post("", status_code=201)
def create_worker(data: WorkerCreate, db: Session = Depends(get_db)):
    worker = Worker(**data.dict())
    db.add(worker)
    db.commit()
    db.refresh(worker)
    return {"success": True}
