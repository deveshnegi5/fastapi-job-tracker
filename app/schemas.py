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

class UserCreate(BaseModel):
    email: str
    password: str

class UserOut(BaseModel):
    id: int
    email: str

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"