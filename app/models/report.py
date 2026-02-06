from sqlalchemy import Column, Integer, String, ForeignKey
from app.database import Base

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    worker_id = Column(Integer, ForeignKey("workers.id"), nullable=False)
    reason = Column(String, nullable=False)
    description = Column(String, nullable=True)

    status = Column(String, default="pending")  
    # pending | ignored | warned | banned
