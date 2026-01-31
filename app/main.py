from fastapi import FastAPI
from app.routers import auth, jobs
from app.database import Base, engine
from app.models import user, job  # IMPORTANT
from app.routers import workers

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Jobsify backend running"}

# 🔥 CREATE TABLES
Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(jobs.router)

app.include_router(workers.router)
