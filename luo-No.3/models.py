from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, declarative_base

# 声明基础类
Base = declarative_base()

class Student(Base):
    __tablename__ = 'students'

    id = Column(Integer, primary_key=True)
    name = Column(String(32), nullable=False)
    sno = Column(Integer, nullable=False)

    # 定义多对多关系
    groups = relationship('Group', secondary='student_group', back_populates='students')

class Group(Base):
    __tablename__ = 'groups'

    id = Column(Integer, primary_key=True)
    name = Column(String(32), nullable=False)

    # 定义多对多关系
    students = relationship('Student', secondary='student_group', back_populates='groups')

# 中间表，用于多对多关系
class StudentGroup(Base):
    __tablename__ = 'student_group'

    student_id = Column(Integer, ForeignKey('students.id'), primary_key=True)
    group_id = Column(Integer, ForeignKey('groups.id'), primary_key=True)

# 创建数据库引擎，确保与主应用代码一致
def get_engine(database_url):
    return create_engine(database_url)

# 示例用法
if __name__ == '__main__':
    from settings import get_database_url

    DATABASE_CONFIG = {
        'dialect': 'mysql+pymysql',
        'username': 'root',
        'password': 'HYW',
        'host': '127.0.0.1',
        'port': '3306',
        'database': 'houyanwu',
    }

    DATABASE_URL = get_database_url(DATABASE_CONFIG)
    engine = get_engine(DATABASE_URL)

    # 创建所有表
    Base.metadata.create_all(engine)


