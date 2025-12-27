from fastapi import FastAPI
from app.routers import auth, jobs

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Jobsify backend running"}

app.include_router(auth.router)
app.include_router(jobs.router)
