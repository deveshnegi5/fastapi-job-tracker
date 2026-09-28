from pydantic import BaseModel, ConfigDict
from datetime import datetime

class ApplicationCreate(BaseModel):
    company: str
    role:str
    status: str="applied"

class Applicationout(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company:str
    role: str
    status:str
    created_at: datetime

class UserCreate(BaseModel):
    email: str
    password: str

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
