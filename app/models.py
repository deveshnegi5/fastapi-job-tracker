from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.database import Base

class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    company= Column(String, nullable=False)
    role = Column(String, nullable=False)
    status =Column(String, default="applied")
    created_at = Column(DateTime(timezone=True),server_default=func.now())