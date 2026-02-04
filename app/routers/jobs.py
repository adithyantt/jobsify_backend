from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.job import Job
from app.schemas.job import JobCreate, JobResponse

router = APIRouter()

# ---------------- USER SIDE ----------------

# ✅ GET ALL VERIFIED JOBS (PUBLIC)
@router.get("/jobs", response_model=List[JobResponse])
def get_jobs(db: Session = Depends(get_db)):
    return (
        db.query(Job)
        .filter(Job.verified == True)   # ✅ ONLY VERIFIED JOBS
        .order_by(Job.id.desc())
        .all()
    )

    return (
        db.query(Job)
        .filter(Job.verified == True)
        .order_by(Job.id.desc())
        .all()
    )


# ✅ CREATE JOB (DEFAULT = NOT VERIFIED)
@router.post("/jobs", response_model=JobResponse)
def create_job(job: JobCreate, db: Session = Depends(get_db)):
    new_job = Job(
        title=job.title,
        category=job.category,
        description=job.description,
        location=job.location,
        phone=job.phone,
        latitude=job.latitude,
        longitude=job.longitude,
        urgent=job.urgent,
        verified=False,  # ❗ admin must verify
        salary=job.salary,
    )

    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    return new_job


# ---------------- ADMIN SIDE ----------------

# ✅ GET ALL PENDING JOBS (ADMIN)
@router.get("/admin/jobs/pending", response_model=List[JobResponse])
def get_pending_jobs(db: Session = Depends(get_db)):
    return (
        db.query(Job)
        .filter(Job.verified == False)
        .order_by(Job.id.desc())
        .all()
    )


# ✅ VERIFY A JOB (ADMIN)
@router.put("/admin/jobs/verify/{job_id}")
def verify_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    job.verified = True
    db.commit()

    return {
        "message": "Job verified successfully",
        "job_id": job_id
    }


# ❌ OPTIONAL: DELETE / REJECT JOB (ADMIN)
@router.delete("/admin/jobs/{job_id}")
def delete_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    db.delete(job)
    db.commit()

    return {"message": "Job deleted successfully"}

@router.put("/jobs/{job_id}/verify")
def verify_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    job.verified = True
    db.commit()
    db.refresh(job)

    return {
        "message": "Job verified successfully",
        "job_id": job.id
    }
@router.get("/admin/stats")
def admin_stats(db: Session = Depends(get_db)):
    total_jobs = db.query(Job).count()
    verified_jobs = db.query(Job).filter(Job.verified == True).count()
    pending_jobs = db.query(Job).filter(Job.verified == False).count()

    return {
        "total_jobs": total_jobs,
        "verified_jobs": verified_jobs,
        "pending_jobs": pending_jobs
    }
