from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.database import Base, engine
import traceback

# Import models to ensure they are registered with SQLAlchemy
from app.models.user import User
from app.models.job import Job
from app.models.workers import Worker
from app.models.report import Report
from app.models.review import Review


from app.routers import auth, jobs, workers, reports, reviews
from app.routers import admin_reports, admin_workers, notifications, admin


app = FastAPI()

# Global exception handler to catch all errors
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print(f"GLOBAL ERROR: {exc}")
    print(f"TRACE: {traceback.format_exc()}")
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"}
    )


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
app.include_router(reviews)
app.include_router(admin_reports)
app.include_router(admin_workers)
app.include_router(notifications)
app.include_router(admin)
