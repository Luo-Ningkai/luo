import uvicorn
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine
from settings import get_database_url
from models import Student, Group, StudentGroup, Base
from student import student_api, group_api

# 数据库配置
DATABASE_CONFIG = {
    'dialect': 'mysql+pymysql',
    'username': 'root',
    'password': 'HYW',
    'host': '127.0.0.1',
    'port': '3306',
    'database': 'houyanwu',
}

# 获取数据库连接字符串
DATABASE_URL = get_database_url(DATABASE_CONFIG)

# 创建数据库引擎和会话
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建FastAPI应用
app = FastAPI()

# 创建数据库会话依赖
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 注册路由
app.include_router(student_api, prefix="/students")
app.include_router(group_api, prefix="/groups", tags=["groups"])

# 运行应用
if __name__ == '__main__':
    uvicorn.run('main:app', host='127.0.0.1', port=8000, reload=True, workers=1)

