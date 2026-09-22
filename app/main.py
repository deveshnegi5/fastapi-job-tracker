from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from app.database import Base, engine,get_db
from app.dependencies import current_user
from app.security import hash_password, verify_password, create_access_token
from app.models import Application, User
from sqlalchemy.orm import Session
from app import schemas


app=FastAPI()

# Base.metadata.create_all(bind=engine)
@app.get("/")
def root():
    return {
        "status":"ok"
    }

@app.post("/register", response_model=schemas.UserOut)
def register(data: schemas.UserCreate, db: Session= Depends(get_db)):
    existing=db.query(User).filter(User.email==data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")
    user=User(email=data.email,hashed_password= hash_password(data.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@app.post("/login", response_model=schemas.Token)
def login(form: OAuth2PasswordRequestForm= Depends(), db: Session=Depends(get_db)):
    user= db.query(User).filter(User.email==form.username).first()
    if not user or not verify_password(form.password,user.hashed_password):
        raise HTTPException(status_code=401,detail="Invalid credentials")
    token = create_access_token({"sub":str(user.id)})
    return {"access_token":token, "token_type": "bearer"}


@app.post("/applications", response_model=schemas.Applicationout)
def add_data(data: schemas.ApplicationCreate,db:Session=Depends(get_db),user:User= Depends(current_user)):
    app=Application(**data.model_dump(), user_id=user.id)
    db.add(app)
    db.commit()
    db.refresh(app)
    return app

@app.get("/applications", response_model=list[schemas.Applicationout])
def get_data(db:Session= Depends(get_db), user:User= Depends(current_user)):
    app= db.query(Application).filter(Application.user_id == user.id).all()
    if not app:
        raise HTTPException(
            status_code= 404,
            detail="no data available"
        )
    return app

@app.get("/get/{app_id}", response_model=schemas.Applicationout)
def get_data_id(app_id: int, db: Session = Depends(get_db),user: User=Depends(current_user)):
    app = db.query(Application).filter(
        Application.id == app_id, 
        Application.user_id == user.id).first()
    if not app:
        raise HTTPException(status_code=404, detail=f"ID {app_id} not found")
    return app

@app.put("/update/{app_id}", response_model=schemas.Applicationout)
def update(app_id: int, data: schemas.ApplicationCreate, db: Session = Depends(get_db), user:User=Depends(current_user)):
    app=db.query(Application).filter(Application.user_id == user.id).first()
    if not app:
        raise HTTPException(
            status_code=404,
            detail=f"ID {app_id} not found"
        )
    for key, value in data.model_dump().items():
        setattr(app,key, value)
    db.commit()
    db.refresh(app)
    return app

@app.delete("/delete/{app_id}")
def delete(app_id: int, db: Session = Depends(get_db),user:User=Depends(current_user)):

    app= db.query(Application).filter(Application.user_id == user.id).first()
    if not app:
        raise HTTPException(
            status_code=404,
            detail="not found"
        )
    db.delete(app)
    db.commit()
    return {"message": f"Deleted id {app_id}"}
