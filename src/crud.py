from sqlalchemy.orm import Session
from . import models, schemas

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    fake_hashed_password = user.password + "notreallyhashed"
    db_user = models.User(email=user.email, password=fake_hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_tasks_by_owner_id(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Task).filter(models.Task.owner_id == user_id).offset(skip).limit(limit).all()

def get_task_by_owner_id_and_task_id(db: Session, user_id: int, task_id: int):
    return db.query(models.Task).filter(models.Task.id == task_id and models.Task.owner_id == user_id).first()

def create_user_task(db: Session, task: schemas.TaskCreate, user_id: int):
    db_task = models.Task(**task.dict(), owner_id=user_id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def update_user_task(db: Session, task: schemas.TaskCreate, user_id: int, task_id: int):
    db_task = get_task_by_owner_id_and_task_id(db, user_id, task_id)
    db_task.name = task.name
    db_task.comment = task.comment
    db_task.done = task.done
    db.commit()
    return db_task

def delete_user_task(db: Session, user_id: int, task_id: int):
    db_task = get_task_by_owner_id_and_task_id(db, user_id, task_id)
    db.delete(db_task)
    db.commit()