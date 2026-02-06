from app.database import Base, engine

# 👇 IMPORT ALL MODELS YOU WANT TABLES FOR
from app.models.user import User
from app.models.job import Job
from app.models.workers import Worker
from app.models.report import Report

print("Creating database tables...")
Base.metadata.create_all(bind=engine)
print("Done.")
