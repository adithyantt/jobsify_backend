from fastapi import FastAPI
from app.database import engine, Base
from app.models import user, job
from app.routers import auth,jobs

app = FastAPI(title="Jobsify Backend")

# create all database tables
Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"message": "Jobsify backend running"}

#Include routers
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(jobs.router, prefix="/jobs", tags=["Jobs"])
