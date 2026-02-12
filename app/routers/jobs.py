from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.job import Job, SavedJob
from app.models.report import Report
from app.models.notification import Notification
from app.models.user import User
from app.schemas.job import JobCreate, JobResponse, SavedJobCreate, SavedJobResponse
from app.schemas.report import ReportCreate, ReportResponse
from app.routers.auth import get_current_admin

router = APIRouter(prefix="/jobs", tags=["Jobs"])


# ---------------- USER SIDE ----------------

# =====================================================
# 👤 USER SIDE – GET ONLY VERIFIED JOBS
# =====================================================
@router.get("", response_model=list[JobResponse])
def get_jobs(db: Session = Depends(get_db)):
    try:
        jobs = (
            db.query(Job)
            .filter(Job.verified == True)
            .order_by(Job.id.desc())
            .all()
        )
        return jobs
    except Exception as e:
        print(f"ERROR in get_jobs: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


# =====================================================
# 👤 USER SIDE – GET MY JOBS (BY EMAIL)
# =====================================================
@router.get("/my", response_model=list[JobResponse])
def get_my_jobs(email: str = Query(..., description="User email"), db: Session = Depends(get_db)):
    print(f"DEBUG: get_my_jobs called with email={email}")
    try:
        if not email or email.strip() == "":
            raise HTTPException(status_code=400, detail="Email parameter is required")
        
        # Validate email format
        email = email.strip().lower()
        if "@" not in email:
            raise HTTPException(status_code=400, detail="Invalid email format")
        
        # Check if Job model has user_email attribute
        if not hasattr(Job, 'user_email'):
            print("ERROR: Job model does not have user_email attribute")
            raise HTTPException(status_code=500, detail="Server configuration error: missing user_email field")
        
        # Query jobs with error handling
        try:
            jobs = (
                db.query(Job)
                .filter(Job.user_email == email)
                .order_by(Job.id.desc())
                .all()
            )
            print(f"DEBUG: Found {len(jobs)} jobs for email={email}")
            return jobs
        except Exception as query_error:
            print(f"ERROR in database query: {query_error}")
            # Try to get more details about the error
            import traceback
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f"Database query error: {str(query_error)}")
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR in get_my_jobs: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")




# =====================================================
# 👤 USER SIDE – CREATE JOB
# (DEFAULT: verified = False)
# =====================================================
@router.post("", response_model=JobResponse)
def create_job(job: JobCreate, db: Session = Depends(get_db)):
    try:
        print(f"DEBUG: Creating job with data: {job.model_dump()}")
        
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
            urgent=job.urgent if job.urgent is not None else False,
            salary=job.salary,
        )

        db.add(new_job)
        db.commit()
        db.refresh(new_job)
        
        print(f"DEBUG: Job created successfully with ID: {new_job.id}")

        return new_job
        
    except Exception as e:
        print(f"ERROR in create_job: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create job: {str(e)}")


# =====================================================
# 🛡️ ADMIN SIDE – GET PENDING JOBS
# =====================================================
@router.get("/admin/pending", response_model=list[JobResponse])
def get_pending_jobs(db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin)):
    return (
        db.query(Job)
        .filter(Job.verified == False)
        .order_by(Job.id.desc())
        .all()
    )


# =====================================================
# 🛡️ ADMIN SIDE – APPROVE JOB
# =====================================================
@router.put("/admin/approve/{job_id}")
def approve_job(job_id: int, db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin)):

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
def reject_job(job_id: int, db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin)):

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


# =====================================================
# 👤 USER SIDE – SAVE JOB
# =====================================================
@router.post("/save", response_model=SavedJobResponse)
def save_job(saved_job: SavedJobCreate, db: Session = Depends(get_db)):
    try:
        # Check if job exists
        job = db.query(Job).filter(Job.id == saved_job.job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        # Check if already saved
        existing = db.query(SavedJob).filter(
            SavedJob.user_email == saved_job.user_email,
            SavedJob.job_id == saved_job.job_id
        ).first()

        if existing:
            raise HTTPException(status_code=400, detail="Job already saved")

        new_saved_job = SavedJob(
            user_email=saved_job.user_email,
            job_id=saved_job.job_id
        )

        db.add(new_saved_job)
        db.commit()
        db.refresh(new_saved_job)

        return new_saved_job
    except HTTPException:
        raise
    except Exception as e:
        print(f"Exception in save_job: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to save job: {str(e)}")


# =====================================================
# 👤 USER SIDE – UNSAVE JOB
# =====================================================
@router.delete("/save/{job_id}")
def unsave_job(job_id: int, email: str = Query(...), db: Session = Depends(get_db)):
    try:
        saved_job = db.query(SavedJob).filter(
            SavedJob.job_id == job_id,
            SavedJob.user_email == email
        ).first()

        if not saved_job:
            raise HTTPException(status_code=404, detail="Saved job not found")

        db.delete(saved_job)
        db.commit()

        return {"message": "Job unsaved successfully"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Exception in unsave_job: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to unsave job: {str(e)}")


# =====================================================
# 👤 USER SIDE – GET SAVED JOBS
# =====================================================
@router.get("/saved", response_model=list[JobResponse])
def get_saved_jobs(email: str = Query(...), db: Session = Depends(get_db)):
    try:
        saved_jobs = (
            db.query(Job)
            .join(SavedJob, Job.id == SavedJob.job_id)
            .filter(SavedJob.user_email == email)
            .filter(Job.verified == True)
            .order_by(SavedJob.saved_at.desc())
            .all()
        )

        return saved_jobs
    except Exception as e:
        print(f"Exception in get_saved_jobs: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to get saved jobs: {str(e)}")


# =====================================================
# 👤 USER SIDE – CHECK IF JOB IS SAVED
# =====================================================
@router.get("/saved/{job_id}")
def check_saved_job(job_id: int, email: str = Query(...), db: Session = Depends(get_db)):
    try:
        saved_job = db.query(SavedJob).filter(
            SavedJob.job_id == job_id,
            SavedJob.user_email == email
        ).first()

        return {"is_saved": saved_job is not None}
    except Exception as e:
        print(f"Exception in check_saved_job: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to check saved job: {str(e)}")
