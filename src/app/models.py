from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import expression

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    # MySQLではVARCHAR型にlengthが必要
    name = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String(500), nullable=False)

    tasks = relationship("Task", back_populates="owner")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    comment = Column(String(500), index=True)
    done = Column(Boolean, server_default=expression.false(),
                  default=False, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    owner = relationship("User", back_populates="tasks")
