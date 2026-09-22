from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.security import decode_access_token
from app import models

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def current_user(token: str= Depends(oauth2_scheme), db : Session = Depends(get_db)):
    try:
        payload= decode_access_token(token)
        # print(payload)
        user_id = payload.get("sub")
    except Exception:
        raise HTTPException( status_code= 401, detail="Invalid or expired token")
    user = db.query(models.User).filter(models.User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user