from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

DATABASE_URL = 'mysql+pymysql://root:Liu94326@localhost:3306/hello-auth'

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'  # 指定表名

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(320), unique=True, index=True)
    hashed_password = Column(String(100))
    role = Column(String(50), default='user')  # 添加用户角色
    login_histories = relationship("LoginHistory", back_populates="user")

class LoginHistory(Base):
    __tablename__ = 'login_histories'  # 指定表名

    id = Column(Integer, primary_key=True, index=True)
    user_agent = Column(String(255))
    datetime = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="login_histories")

Base.metadata.create_all(bind=engine)
