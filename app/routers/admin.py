
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User
from app.models.job import Job
from app.models.workers import Worker
from app.models.report import Report
from app.schemas.user import UserResponse
from app.routers.auth import get_current_admin

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/stats")
def get_admin_stats(db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin)):
    try:
        pending_jobs = db.query(Job).filter(Job.verified == False).count()
        providers = db.query(Worker).filter(Worker.is_verified == False).count()
        users = db.query(User).count()
        # Use func.count to avoid loading all columns (fixes missing column issues)
        from sqlalchemy import func
        reports = db.query(func.count(Report.id)).scalar() or 0
        return {
            "pending_jobs": pending_jobs,
            "providers": providers,
            "users": users,
            "reports": reports
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users", response_model=List[UserResponse])
def get_all_users(db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin)):
    return db.query(User).all()

@router.put("/users/block")
def block_user(user_id: int, db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.blocked = True
    db.commit()
    return {"message": "User blocked successfully"}
