from pydantic import BaseModel
from datetime import datetime

class ApplicationCreate(BaseModel):
    company: str
    role:str
    status: str="applied"

class Applicationout(BaseModel):
    id: int
    company:str
    role: str
    status:str
    created_at: datetime

    class Config:
        from_attributes = True
