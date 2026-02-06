from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.job import Job
from app.schemas.job import JobCreate, JobResponse

router = APIRouter(tags=["Jobs"])


# ✅ GET ALL JOBS
# 👤 USER SIDE – only approved jobs
@router.get("/jobs", response_model=list[JobResponse])
def get_jobs(db: Session = Depends(get_db)):
    return db.query(Job).filter(Job.is_verified == True).all()



# ✅ CREATE JOB
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
    )

    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    return new_job

@router.get("/admin/jobs/pending", response_model=list[JobResponse])
def get_pending_jobs(db: Session = Depends(get_db)):
    return db.query(Job).filter(Job.is_verified == False).all()

@router.put("/admin/jobs/approve/{job_id}")
def approve_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()

    if not job:
        return {"error": "Job not found"}

    job.is_verified = True
    db.commit()

    return {"message": "Job approved"}
