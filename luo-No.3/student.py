from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Union
from models import Student, Group  # 确保 Group 模型也被导入
from database import get_db  # 假设你有一个获取数据库会话的函数

# 创建API路由
student_api = APIRouter()
group_api = APIRouter()


# Pydantic模型定义
class GroupModel(BaseModel):
    id: int
    name: str


class StudentModel(BaseModel):
    name: str
    id: int
    sno: int
    group_id: Union[int, None] = None


class AddStudentsToGroupModel(BaseModel):
    id: int
    student_ids: List[int]


class RemoveStudentModel(BaseModel):
    student_ids: List[int]


class StudentResponseModel(BaseModel):
    id: int
    name: str
    sno: int


class TransferStudentModel(BaseModel):
    student_id: int


# 学生API
@student_api.get("/", response_model=List[StudentResponseModel])
async def get_all_students(db: Session = Depends(get_db)):
    students = db.query(Student).all()  # 获取所有学生
    return [StudentResponseModel(id=student.id, name=student.name, sno=student.sno) for student in students]


@student_api.get("/{id}", response_model=StudentResponseModel)
async def get_student(id: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return StudentResponseModel(id=student.id, name=student.name, sno=student.sno)


@student_api.post("/", response_model=StudentResponseModel)
async def create_student(student_model: StudentModel, db: Session = Depends(get_db)):
    student = Student(**student_model.dict())
    db.add(student)
    db.commit()
    db.refresh(student)
    return StudentResponseModel(id=student.id, name=student.name, sno=student.sno)


@student_api.delete("/{id}")
async def delete_student(id: int, db: Session = Depends(get_db)):
    deleted_student = db.query(Student).filter(Student.id == id).delete()
    db.commit()
    if deleted_student == 0:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"message": "success"}


@student_api.post("/groups/{group_id}/students/")
async def add_students_to_group(group_id: int, group_model: AddStudentsToGroupModel, db: Session = Depends(get_db)):
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    students = db.query(Student).filter(Student.id.in_(group_model.student_ids)).all()
    group.students.extend(students)  # 假设 Group 有一个 students 属性
    db.commit()

    return {"message": "Students added to group successfully."}


@student_api.delete("/groups/{group_id}/students/")
async def remove_students_from_group(group_id: int, remove_model: RemoveStudentModel, db: Session = Depends(get_db)):
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    students_to_remove = db.query(Student).filter(Student.id.in_(remove_model.student_ids)).all()
    for student in students_to_remove:
        group.students.remove(student)  # 假设 Group 有一个 students 属性
    db.commit()

    return {"message": "Students removed from group successfully."}


@student_api.get("/groups/{group_id}/students/", response_model=List[StudentResponseModel])
async def get_students_in_group(group_id: int, db: Session = Depends(get_db)):
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    return [StudentResponseModel(id=student.id, name=student.name, sno=student.sno) for student in group.students]


@student_api.post("/groups/{from_group_id}/transfer/{to_group_id}/")
async def transfer_student(from_group_id: int, to_group_id: int, transfer_model: TransferStudentModel,
                           db: Session = Depends(get_db)):
    from_group = db.query(Group).filter(Group.id == from_group_id).first()
    to_group = db.query(Group).filter(Group.id == to_group_id).first()
    student = db.query(Student).filter(Student.id == transfer_model.student_id).first()

    if not from_group or not to_group:
        raise HTTPException(status_code=404, detail="One of the groups not found.")

    if student not in from_group.students:
        raise HTTPException(status_code=400, detail="Student not found in the source group.")

    from_group.students.remove(student)
    to_group.students.append(student)
    db.commit()

    return {"message": "Student transferred successfully."}


# 组API
@group_api.get("/", response_model=List[GroupModel])
async def get_all_groups(db: Session = Depends(get_db)):
    groups = db.query(Group).all()
    return groups


@group_api.get("/{id}", response_model=GroupModel)
async def get_group(id: int, db: Session = Depends(get_db)):
    group = db.query(Group).filter(Group.id == id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    return group


@group_api.post("/", response_model=GroupModel)
async def create_group(group_model: GroupModel, db: Session = Depends(get_db)):
    group = Group(**group_model.dict())
    db.add(group)
    db.commit()
    db.refresh(group)
    return group


@group_api.delete("/{id}")
async def delete_group(id: int, db: Session = Depends(get_db)):
    deleted_group = db.query(Group).filter(Group.id == id).delete()
    db.commit()
    if deleted_group == 0:
        raise HTTPException(status_code=404, detail="Group not found")
    return {"message": "Group deleted successfully."}

