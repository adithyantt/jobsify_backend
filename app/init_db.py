from .database import Base, engine

# 👇 IMPORT ALL MODELS YOU WANT TABLES FOR
from .models.user import User
from .models.job import Job
from .models.workers import Worker
from .models.report import Report

print("Creating database tables...")
Base.metadata.create_all(bind=engine)
print("Done.")
