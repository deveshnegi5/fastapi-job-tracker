from sqlalchemy import Column, Integer, String, DateTime,ForeignKey,UniqueConstraint
from sqlalchemy.sql import func
from app.database import Base

class Job(Base):
    __tablename__ = "jobs"
    __table_args__ = (UniqueConstraint("url",name="uq_job_url"),)

    id =Column(Integer,primary_key=True,index=True)
    title=Column(String,nullable=False)
    company=Column(String,nullable=False)
    url = Column(String,nullable=True)
    scraped_at=Column(DateTime(timezone=True),server_default=func.now())

class User(Base):
    __tablename__=  "users"

    id = Column(Integer,primary_key=True,index=True)
    email= Column(String,unique=True,index=True,nullable=False)
    hashed_password= Column(String,nullable=False)


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    company= Column(String, nullable=False)
    role = Column(String, nullable=False)
    status =Column(String, default="applied")
    created_at = Column(DateTime(timezone=True),server_default=func.now())
    user_id = Column(Integer,ForeignKey("users.id"), nullable=False)