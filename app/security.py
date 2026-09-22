import os
import jwt
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext

SECRET_KEY= os.getenv("SECRET_KEY")
ALGORITHM="HS256"
access_token_expire_minute=10

pwd_context= CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password:str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password:str) -> bool:
    return pwd_context.verify(plain_password,hashed_password)

def create_access_token(data:dict) -> str:
    to_encode = data.copy()
    to_encode["exp"]= datetime.now(timezone.utc) + timedelta(minutes=access_token_expire_minute)
    return jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)

def decode_access_token(token:str)->dict:
    return jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])