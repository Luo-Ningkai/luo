
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from models import Base

SQLALCHEMY_DATABASE_URL =  SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:HYW@127.0.0.1:3306/houyanwu"


engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
