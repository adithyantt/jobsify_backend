from fastapi import FastAPI
from app.database import Base, engine

from app.routers import auth, jobs, workers, reports
from app.routers import admin_reports
app = FastAPI()

@app.get("/")
def root():
    return {"message": "Jobsify backend running"}

Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(jobs.router)
app.include_router(workers.router)
app.include_router(reports.router)
app.include_router(admin_reports.router)