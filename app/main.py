from fastapi import FastAPI, Depends, HTTPException
from app.database import Base, engine,get_db
from app.models import Application
from sqlalchemy.orm import Session
from app import schemas


app=FastAPI()

Base.metadata.create_all(bind=engine)
@app.get("/")
def root():
    return {
        "status":"ok"
    }

@app.post("/applications", response_model=schemas.Applicationout)
def add_data(data: schemas.ApplicationCreate,db:Session=Depends(get_db)):
    app=Application(**data.model_dump())
    db.add(app)
    db.commit()
    db.refresh(app)
    return app

@app.get("/applications", response_model=list[schemas.Applicationout])
def get_data(db:Session= Depends(get_db)):
    app= db.query(Application).order_by(Application.id).all()
    if not app:
        raise HTTPException(
            status_code= 404,
            detail="no data available"
        )
    return app

@app.get("/get/{app_id}", response_model=schemas.Applicationout)
def get_data_id(app_id: int, db: Session = Depends(get_db)):
    app = db.query(Application).filter(Application.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail=f"ID {app_id} not found")
    return app

@app.put("/update/{app_id}", response_model=schemas.Applicationout)
def update(app_id: int, data: schemas.ApplicationCreate, db: Session = Depends(get_db)):
    app=db.query(Application).filter(Application.id == app_id).first()
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
def delete(app_id: int, db: Session = Depends(get_db)):

    app= db.query(Application).filter(Application.id == app_id).first()
    if not app:
        raise HTTPException(
            status_code=404,
            detail="not found"
        )
    db.delete(app)
    db.commit()
    return {"message": f"Deleted id {app_id}"}
