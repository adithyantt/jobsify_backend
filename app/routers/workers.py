from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.workers import Worker
from app.models.report import Report
from app.models.notification import Notification
from app.models.user import User
from app.schemas.workers import WorkerCreate, WorkerResponse
from app.schemas.report import ReportCreate, ReportResponse
from app.routers.auth import get_current_admin


router = APIRouter(prefix="/workers", tags=["Workers"])


def _normalize_email(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    value = value.strip().lower()
    return value or None


def _serialize_worker(worker: Worker, viewer_email: Optional[str] = None) -> dict:
    owner_email = _normalize_email(worker.user_email)
    viewer_email = _normalize_email(viewer_email)
    is_owner = viewer_email is not None and viewer_email == owner_email
    return {
        "id": worker.id,
        "first_name": worker.first_name,
        "last_name": worker.last_name,
        "name": worker.name,
        "role": worker.role,
        "phone": worker.phone,
        "experience": worker.experience,
        "location": worker.location,
        "latitude": worker.latitude,
        "longitude": worker.longitude,
        "user_email": worker.user_email,
        "availability_type": worker.availability_type,
        "available_days": worker.available_days,
        "rating": worker.rating,
        "reviews": worker.reviews,
        "is_available": worker.is_available,
        "is_verified": worker.is_verified,
        "is_owner": is_owner,
        "can_message": not is_owner,
    }

# 🔹 GET VERIFIED & AVAILABLE WORKERS (WITH FILTERING AND PAGINATION)
@router.get("")
def get_workers(
    db: Session = Depends(get_db),
    viewer_email: Optional[str] = Query(None, description="Logged-in user email for ownership flags"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    min_experience: Optional[int] = Query(None, description="Minimum years of experience"),
    max_experience: Optional[int] = Query(None, description="Maximum years of experience"),
    min_rating: Optional[float] = Query(None, description="Minimum rating (0-5)"),
    location: Optional[str] = Query(None, description="Filter by location (partial match)"),
    availability_type: Optional[str] = Query(None, description="Filter by availability type: everyday, selected_days, not_available"),
    available_days: Optional[str] = Query(None, description="Filter by specific days (comma-separated: Mon,Tue,Wed)"),
    is_available: Optional[bool] = Query(None, description="Filter by availability"),
    sort_by: Optional[str] = Query("distance", description="Sort by: distance, experience_high, experience_low, rating_high, rating_low")
):
    query = db.query(Worker).filter(Worker.is_verified == True)
    
    # Apply availability filter
    if is_available is not None:
        query = query.filter(Worker.is_available == is_available)
    else:
        # Default: show only available workers
        query = query.filter(Worker.is_available == True)
    
    # Apply availability type filter
    if availability_type is not None:
        query = query.filter(Worker.availability_type == availability_type)
    
    # Apply available days filter (workers who work on any of the specified days)
    if available_days is not None:
        days_list = [d.strip() for d in available_days.split(",")]
        # Filter workers who have any of the specified days in their available_days
        conditions = [Worker.available_days.ilike(f"%{day}%") for day in days_list]
        from sqlalchemy import or_
        query = query.filter(or_(*conditions))
    
    # Apply experience filters
    if min_experience is not None:
        query = query.filter(Worker.experience >= min_experience)
    if max_experience is not None:
        query = query.filter(Worker.experience <= max_experience)
    
    # Apply rating filter
    if min_rating is not None:
        query = query.filter(Worker.rating >= min_rating)
    
    # Apply location filter
    if location is not None:
        query = query.filter(Worker.location.ilike(f"%{location}%"))
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * limit
    workers = query.order_by(Worker.id.desc()).offset(offset).limit(limit).all()
    
    # Apply sorting (in memory after pagination)
    if sort_by == "experience_high":
        workers.sort(key=lambda w: w.experience or 0, reverse=True)
    elif sort_by == "experience_low":
        workers.sort(key=lambda w: w.experience or 0)
    elif sort_by == "rating_high":
        workers.sort(key=lambda w: w.rating or 0, reverse=True)
    elif sort_by == "rating_low":
        workers.sort(key=lambda w: w.rating or 0)
    
    # Convert SQLAlchemy objects to dictionaries
    workers_list = []
    for worker in workers:
        workers_list.append(_serialize_worker(worker, viewer_email))
    
    return {
        "workers": workers_list,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit
    }


# =====================================================
# 👤 USER SIDE – GET MY WORKERS (BY EMAIL)
# =====================================================

@router.get("/my", response_model=list[WorkerResponse])
def get_my_workers(email: str, db: Session = Depends(get_db)):
    email = _normalize_email(email)
    workers = (
        db.query(Worker)
        .filter(Worker.user_email == email)
        .all()
    )
    return [_serialize_worker(worker, email) for worker in workers]


# =====================================================
# 👤 USER SIDE – GET WORKER BY ID
# =====================================================
@router.get("/{worker_id}", response_model=WorkerResponse)
def get_worker_by_id(
    worker_id: int,
    viewer_email: Optional[str] = Query(None, description="Logged-in user email for ownership flags"),
    db: Session = Depends(get_db),
):
    try:
        worker = db.query(Worker).filter(Worker.id == worker_id).first()
        if not worker:
            raise HTTPException(status_code=404, detail="Worker not found")
        return _serialize_worker(worker, viewer_email)
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR in get_worker_by_id: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


# =====================================================
# 👤 USER SIDE – CREATE WORKER PROFILE
# (DEFAULT: is_verified = False)
# =====================================================
@router.post("", response_model=WorkerResponse)
def create_worker(worker: WorkerCreate, db: Session = Depends(get_db)):
    owner_email = _normalize_email(worker.user_email)
    # Determine is_available based on availability_type
    is_available = worker.availability_type != "not_available"
    
    new_worker = Worker(
        first_name=worker.first_name,
        last_name=worker.last_name,
        name=f"{worker.first_name} {worker.last_name}",  # Combined name for backward compatibility
        role=worker.role,
        phone=worker.phone,
        experience=worker.experience,
        location=worker.location,
        latitude=worker.latitude,
        longitude=worker.longitude,
        user_email=owner_email,
        availability_type=worker.availability_type or "everyday",
        available_days=worker.available_days,
        is_verified=False,     # 🔒 Admin must approve
        is_available=is_available
    )

    db.add(new_worker)
    db.commit()
    db.refresh(new_worker)

    return _serialize_worker(new_worker, owner_email)

# =====================================================
# 🛡️ ADMIN SIDE – GET PENDING WORKERS
# =====================================================
@router.get("/admin/pending", response_model=list[WorkerResponse])
def get_pending_workers(db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin)):
    workers = (
        db.query(Worker)
        .filter(Worker.is_verified == False)
        .all()
    )
    return [_serialize_worker(worker) for worker in workers]

# =====================================================
# 🛡️ ADMIN SIDE – APPROVE WORKER
# =====================================================
@router.put("/admin/approve/{worker_id}")
def approve_worker(worker_id: int, db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin)):
    worker = db.query(Worker).filter(Worker.id == worker_id).first()

    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")

    worker.is_verified = True
    db.commit()

    # Create notification for the user
    notification = Notification(
        user_email=worker.user_email,
        title="Worker Approved",
        message=f"Your worker profile '{worker.name}' has been approved and is now live.",
        type="worker",
        reference_id=worker.id
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
def reject_worker(worker_id: int, db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin)):
    worker = db.query(Worker).filter(Worker.id == worker_id).first()

    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")

    # Create notification for the user before deleting
    notification = Notification(
        user_email=worker.user_email,
        title="Worker Rejected",
        message=f"Your worker profile '{worker.name}' has been rejected by admin.",
        type="worker",
        reference_id=worker.id
    )
    db.add(notification)
    db.commit()


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
    email = _normalize_email(email)
    existing_worker = db.query(Worker).filter(Worker.id == worker_id, Worker.user_email == email).first()

    if not existing_worker:
        raise HTTPException(status_code=404, detail="Worker not found or not owned by user")

    # Update with first_name and last_name for atomicity
    existing_worker.first_name = worker.first_name
    existing_worker.last_name = worker.last_name
    existing_worker.name = f"{worker.first_name} {worker.last_name}"  # Combined for backward compatibility
    existing_worker.role = worker.role
    existing_worker.phone = worker.phone
    existing_worker.experience = worker.experience
    existing_worker.location = worker.location
    existing_worker.latitude = worker.latitude
    existing_worker.longitude = worker.longitude
    existing_worker.availability_type = worker.availability_type or "everyday"
    existing_worker.available_days = worker.available_days
    existing_worker.is_available = worker.availability_type != "not_available"

    db.commit()
    db.refresh(existing_worker)

    return _serialize_worker(existing_worker, email)

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
