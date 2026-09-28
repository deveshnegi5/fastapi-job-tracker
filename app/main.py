from fastapi import FastAPI, Depends, HTTPException,Query,Request,Response
from fastapi.security import OAuth2PasswordRequestForm
from app.database import Base, engine,get_db
from app.dependencies import current_user
from app.security import hash_password, verify_password, create_access_token
from app.models import Application, User
from sqlalchemy.orm import Session
from app import schemas
from typing import Optional
from app.cache_key import lifespan,user_key_builder
from fastapi_cache.decorator import cache
from fastapi_cache import FastAPICache
from time import perf_counter
from logging import getLogger
from redis.exceptions import RedisError

app=FastAPI(lifespan=lifespan)
logger = getLogger(__name__)
ALLOWED_SORT_FIELDS = {"created_at", "company", "role", "status"}


async def invalidate_application_cache():
    try:
        await FastAPICache.clear()
    except RedisError:
        logger.exception("Could not invalidate the application cache")


@app.middleware("http")
async def log_applications_response_time(request: Request, call_next):
    if request.method != "GET" or request.url.path != "/applications":
        return await call_next(request)

    start_time = perf_counter()
    try:
        return await call_next(request)
    finally:
        elapsed_ms = (perf_counter() - start_time) * 1000
        print(f"{request.method} {request.url.path} completed in {elapsed_ms:.2f} ms", flush=True)

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
async def add_data(data: schemas.ApplicationCreate,           db:Session=Depends(get_db),user:User= Depends(current_user)):
    app=Application(**data.model_dump(), user_id=user.id)
    db.add(app)
    db.commit()
    db.refresh(app)
    await invalidate_application_cache()
    return app

@app.get("/applications")
@cache(expire=60, key_builder=user_key_builder)
async def get_data(request:Request,
                   response: Response,
             page: int= Query(1,ge=1),
             size:int=Query(10,ge=1,le=100),
             status: Optional[str]=Query(None),
             sort_by: str=Query("created_at"),
             order: str= Query("desc"),
             db:Session= Depends(get_db), 
             user:User= Depends(current_user)):
    # print("!!! DB QUERY RAN !!!")

    # app= db.query(Application).filter(Application.user_id == user.id).all()
    if sort_by not in ALLOWED_SORT_FIELDS:
        raise HTTPException(status_code=400, detail=f"sort_by is not from {ALLOWED_SORT_FIELDS} fields")
    query = db.query(Application).filter(Application.user_id == user.id)
    if status:
        query=query.filter(Application.status == status)

    sort_column= getattr(Application,sort_by,Application.created_at)
    # print(f"sort_column :{sort_column}")
    if order == "desc":
        query=query.order_by(sort_column.desc())
    else:
        query=query.order_by(sort_column.asc())

    total=query.count()
    items=query.offset((page-1)*size).limit(size).all()
    return {
        "page":page,
        "size":size,
        "total":total,
        "pages":(total+size-1)//size,
        "items":[schemas.Applicationout.model_validate(i) for i in items]
    }

@app.get("/applications/{app_id}", response_model=schemas.Applicationout)
def get_data_id(app_id: int, db: Session = Depends(get_db),user: User=Depends(current_user)):
    app = db.query(Application).filter(
        Application.id == app_id, 
        Application.user_id == user.id).first()
    if not app:
        raise HTTPException(status_code=404, detail=f"ID {app_id} not found")
    return app

@app.put("/applications/{app_id}", response_model=schemas.Applicationout)
async def update(app_id: int, data: schemas.ApplicationCreate, db: Session = Depends(get_db), user:User=Depends(current_user)):
    app = db.query(Application).filter(
        Application.id == app_id,
        Application.user_id == user.id,
    ).first()
    if not app:
        raise HTTPException(
            status_code=404,
            detail=f"ID {app_id} not found"
        )
    for key, value in data.model_dump().items():
        setattr(app,key, value)
    db.commit()
    db.refresh(app)
    await invalidate_application_cache()
    return app

@app.delete("/applications/{app_id}")
async def delete(app_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    app = db.query(Application).filter(
        Application.id == app_id,
        Application.user_id == user.id,
    ).first()
    if not app:
        raise HTTPException(
            status_code=404,
            detail="not found"
        )
    db.delete(app)
    db.commit()
    await invalidate_application_cache()
    return {"message": f"Deleted id {app_id}"}
