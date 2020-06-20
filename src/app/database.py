from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import os
import sys
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))
sys.path.append(BASE_DIR)

SQLALCHEMY_DATABASE_URL = "mysql+pymysql://user:password@db/fast_db"

# mysql
# engine = create_engine(SQLALCHEMY_DATABASE_URL)
engine = create_engine(os.environ["SQLALCHEMY_DATABASE_URL"])

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
