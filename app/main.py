from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine

# Import models to ensure they are registered with SQLAlchemy
from app.models.user import User
from app.models.job import Job
from app.models.workers import Worker
from app.models.report import Report

from app.routers import auth, jobs, workers, reports
from app.routers import admin_reports, admin_workers, notifications, admin

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Jobsify backend running"}

app.include_router(auth)
app.include_router(jobs)
app.include_router(workers)
app.include_router(reports)
app.include_router(admin_reports)
app.include_router(admin_workers)
app.include_router(notifications)
app.include_router(admin)
