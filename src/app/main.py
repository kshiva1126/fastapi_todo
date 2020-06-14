from fastapi.security import OAuth2PasswordBearer
from jwt import PyJWTError
from sqlalchemy.orm import Session
from fastapi import Depends, FastAPI, HTTPException
from starlette import status
from datetime import timedelta

from typing import List
from . import crud, models, schemas, utils
from .database import engine, SessionLocal

from starlette.middleware.cors import CORSMiddleware

import uvicorn

models.Base.metadata.create_all(bind=engine)

ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()
# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/authenticate")

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = utils.decode_access_token(data=token)
        name: str = payload.get("sub")
        if name is None:
            raise credentials_exception
        token_data = schemas.TokenData(name=name)
    except PyJWTError:
        raise credentials_exception
    user = crud.get_user_by_name(db=db, name=token_data.name)
    if user is None:
        raise credentials_exception
    return user

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/user", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db=db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@app.post("/authenticate", response_model=schemas.Token)
def authenticate_user(user: schemas.UserAuthenticate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db=db, email=user.email)
    print(db_user)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Name not existed")
    else:
        is_password_correct = crud.check_name_password(db, user)
        if is_password_correct is False:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password is not correct")
        else:
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = utils.create_access_token(
                data={"sub": user.name},
                expires_delta=access_token_expires
            )
            return {"access_token": access_token, "token_type": "Bearer"}

@app.post("/task", response_model=schemas.Task)
async def create_new_task(
    task: schemas.TaskBase,
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return crud.create_new_task(db=db, task=task, user_id=current_user.id)

@app.get("/task", response_model=List[schemas.Task])
async def get_all_tasks(
    task: schemas.TaskBase,
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return crud.get_all_tasks_by_owner_id(db=db, user_id=current_user.id)

@app.get("/task/{task_id}", response_model=schemas.Task)
async def get_task_by_id(
    task_id,
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return crud.get_task_by_id(db=db, task_id=task_id)

@app.put("/task/{task_id}",response_model=schemas.Task)
async def update_task(
    task_id,
    task: schemas.TaskBase,
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return crud.update_task(db=db, task=task, task_id=task_id)

@app.delete("/task/{task_id}")
async def delete_task(
    task_id,
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return crud.delete_task(db=db, task_id=task_id)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)