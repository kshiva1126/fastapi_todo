from typing import List

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@app.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.post("/users/{user_id}/tasks/", response_model=schemas.Task)
def create_task_for_user(
    user_id: int, task: schemas.TaskCreate, db: Session = Depends(get_db)
):
    return crud.create_user_task(db=db, task=task, user_id=user_id)

@app.get("/users/{user_id}/tasks/", response_model=List[schemas.Task])
def read_tasks(
    user_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    return crud.get_tasks_by_owner_id(db, user_id=user_id, skip=skip, limit=limit)

@app.get("/users/{user_id}/tasks/{task_id}", response_model=schemas.Task)
def read_task(
    user_id: int, task_id: int, db: Session = Depends(get_db)
):
    return crud.get_task_by_owner_id_and_task_id(db, user_id=user_id, task_id=task_id)

@app.put("/users/{user_id}/tasks/{task_id}/", response_model=schemas.Task)
def update_task_for_user(
    user_id: int, task_id: int, task: schemas.TaskCreate, db: Session = Depends(get_db)
):
    return crud.update_user_task(db=db, task=task, user_id=user_id, task_id=task_id)

@app.delete("/users/{user_id}/tasks/{task_id}/")
def delete_task_for_user(
    user_id: int, task_id: int, db: Session = Depends(get_db)
):
    crud.delete_user_task(db=db, user_id=user_id, task_id=task_id)