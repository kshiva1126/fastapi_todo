from typing import Optional
from sqlalchemy.orm import Session
from . import models, schemas
import bcrypt

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_name(db: Session, name: Optional[str]):
    return db.query(models.User).filter(models.User.name == name).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
    db_user = models.User(
        name=user.name,
        email=user.email,
        password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def check_name_password(db: Session, user: schemas.UserAuthenticate):
    db_user: models.User = get_user_by_email(db, email=user.email)
    return bcrypt.checkpw(user.password.encode('utf-8'), db_user.password.encode('utf-8'))

def get_all_tasks_by_owner_id(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Task).filter(models.Task.owner_id == user_id).offset(skip).limit(limit).all()

def get_task_by_id(db: Session, task_id: int):
    return db.query(models.Task).filter(models.Task.id == task_id).first()

def create_new_task(db: Session, task: schemas.TaskCreate, user_id: int):
    db_task = models.Task(**task.dict(), owner_id=user_id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def update_task(db: Session, task: schemas.TaskCreate, task_id: int):
    db_task = get_task_by_id(db, task_id)
    db_task.name = task.name
    db_task.comment = task.comment
    db_task.done = task.done
    db.commit()
    return db_task

def delete_task(db: Session, task_id: int):
    db_task = get_task_by_id(db, task_id)
    db.delete(db_task)
    db.commit()

def update_done(db: Session, task: schemas.TaskCreate, task_id: int):
    db_task = get_task_by_id(db, task_id)
    db_task.done = task.done
    db.commit()
    return db_task