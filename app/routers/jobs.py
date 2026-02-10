from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.job import Job
from app.models.report import Report
from app.models.notification import Notification
from app.schemas.job import JobCreate, JobResponse
from app.schemas.report import ReportCreate, ReportResponse

router = APIRouter(prefix="/jobs", tags=["Jobs"])

# ---------------- USER SIDE ----------------

# =====================================================
# 👤 USER SIDE – GET ONLY VERIFIED JOBS
# =====================================================
@router.get("", response_model=list[JobResponse])
def get_jobs(db: Session = Depends(get_db)):
    return (
        db.query(Job)
        .filter(Job.verified == True)
        .all()
    )


# =====================================================
# 👤 USER SIDE – GET MY JOBS (BY EMAIL)
# =====================================================
@router.get("/my", response_model=list[JobResponse])
def get_my_jobs(email: str, db: Session = Depends(get_db)):
    return (
        db.query(Job)
        .filter(Job.user_email == email)
        .all()
    )


# =====================================================
# 👤 USER SIDE – CREATE JOB
# (DEFAULT: verified = False)
# =====================================================
@router.post("", response_model=JobResponse)
def create_job(job: JobCreate, db: Session = Depends(get_db)):
    new_job = Job(
        title=job.title,
        category=job.category,
        description=job.description,
        location=job.location,
        phone=job.phone,
        latitude=job.latitude,
        longitude=job.longitude,
        user_email=job.user_email,  # Add user email
        verified=False,   # 🔒 Admin approval required
        urgent=job.urgent,
        salary=job.salary,
    )

    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    return new_job


# ---------------- ADMIN SIDE ----------------

# =====================================================
# 🛡️ ADMIN SIDE – GET PENDING JOBS
# =====================================================
@router.get("/admin/pending", response_model=list[JobResponse])
def get_pending_jobs(db: Session = Depends(get_db)):
    return (
        db.query(Job)
        .filter(Job.verified == False)
        .all()
    )


# =====================================================
# 🛡️ ADMIN SIDE – APPROVE JOB
# =====================================================
@router.put("/admin/approve/{job_id}")
def approve_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    job.verified = True
    db.commit()

    # Create notification for the user
    notification = Notification(
        user_email=job.user_email,
        title="Job Approved",
        message=f"Your job '{job.title}' has been approved and is now live."
    )
    db.add(notification)
    db.commit()

    return {
        "message": "Job approved successfully",
        "job_id": job_id
    }


# =====================================================
# 🛡️ ADMIN SIDE – REJECT JOB
# =====================================================
@router.put("/admin/reject/{job_id}")
def reject_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Create notification for the user before deleting
    notification = Notification(
        user_email=job.user_email,
        title="Job Rejected",
        message=f"Your job '{job.title}' has been rejected."
    )
    db.add(notification)
    db.commit()

    db.delete(job)
    db.commit()

    return {
        "message": "Job rejected and deleted successfully",
        "job_id": job_id
    }


# =====================================================
# 👤 USER SIDE – UPDATE JOB
# =====================================================
@router.put("/{job_id}", response_model=JobResponse)
def update_job(job_id: int, job: JobCreate, email: str = Query(...), db: Session = Depends(get_db)):
    existing_job = db.query(Job).filter(Job.id == job_id, Job.user_email == email).first()

    if not existing_job:
        raise HTTPException(status_code=404, detail="Job not found or not owned by user")

    existing_job.title = job.title
    existing_job.category = job.category
    existing_job.description = job.description
    existing_job.location = job.location
    existing_job.phone = job.phone
    existing_job.latitude = job.latitude
    existing_job.longitude = job.longitude

    db.commit()
    db.refresh(existing_job)

    return existing_job


# =====================================================
# 👤 USER SIDE – DELETE JOB
# =====================================================
@router.delete("/{job_id}")
def delete_job(job_id: int, email: str = Query(...), db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id, Job.user_email == email).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found or not owned by user")

    db.delete(job)
    db.commit()

    return {
        "message": "Job deleted successfully",
        "job_id": job_id
    }


# =====================================================
# 👤 USER SIDE – REPORT JOB
# =====================================================
@router.post("/report", response_model=ReportResponse)
def report_job(report: ReportCreate, db: Session = Depends(get_db)):
    print("report_job called")
    try:
        print(f"Received report: {report}")
        # Check if job exists
        if report.job_id is None:
            raise HTTPException(status_code=400, detail="job_id is required for job reports")

        job = db.query(Job).filter(Job.id == report.job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        print("Job found, creating report")
        new_report = Report(
            job_id=report.job_id,
            reporter_email=report.reporter_email,
            reason=report.reason,
            description=report.description,
            status="pending"
        )

        print("Adding report to db")
        db.add(new_report)
        print("Committing")
        db.commit()
        print("Refreshing")
        db.refresh(new_report)
        print("Returning report")

        return new_report
    except Exception as e:
        print(f"Exception in report_job: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create report: {str(e)}")


# Additional admin routes
@router.put("/{job_id}/verify")
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
