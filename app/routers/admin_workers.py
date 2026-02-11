from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.workers import Worker
from app.models.user import User
from app.schemas.workers import WorkerResponse
from app.routers.auth import get_current_admin
from typing import List

router = APIRouter(prefix="/admin/workers", tags=["Admin Workers"])

@router.get("/pending", response_model=List[WorkerResponse])
def pending_workers(db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin)):

    return db.query(Worker).filter(Worker.is_verified == False).all()

@router.put("/verify/{worker_id}")
def verify_worker(worker_id: int, db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin)):

    worker = db.query(Worker).filter(Worker.id == worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")

    worker.is_verified = True
    db.commit()
    return {"message": "Worker verified"}

@router.delete("/{worker_id}")
def delete_worker(worker_id: int, db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin)):

    worker = db.query(Worker).filter(Worker.id == worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")

    db.delete(worker)
    db.commit()
    return {"message": "Worker deleted"}
