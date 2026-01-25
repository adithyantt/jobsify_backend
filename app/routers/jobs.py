from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.job import Job
from app.schemas.job import JobCreate, JobResponse

router = APIRouter(tags=["Jobs"])


# ✅ GET ALL JOBS
@router.get("/jobs", response_model=list[JobResponse])
def get_jobs(db: Session = Depends(get_db)):
    return db.query(Job).all()


# ✅ CREATE JOB
@router.post("/jobs", response_model=JobResponse)
def create_job(job: JobCreate, db: Session = Depends(get_db)):
    new_job = Job(
        title=job.title,
        category=job.category,
        description=job.description,
        location=job.location,
    )

    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    return new_job
