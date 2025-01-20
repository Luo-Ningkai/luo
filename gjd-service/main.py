import jwt
from fastapi import FastAPI, HTTPException, Depends, Request, BackgroundTasks
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from passlib.context import CryptContext
from datetime import datetime, timedelta
import redis
from auth import get_password_hash, verify_password, encode_auth_token, decode_token
from settings import settings
from models import User, LoginHistory, SessionLocal
from email_utils import send_verification_email  # 假设你有一个发送邮件的模块

redis_client = redis.Redis(host='127.0.0.1', port=6379, db=0)

app = FastAPI()


# 密码强度检查函数
def is_password_strong(password: str) -> bool:
    return len(password) >= 8 and any(char.isdigit() for char in password) and any(char.isupper() for char in password)


@app.post("/register")
async def register(email: str, password: str, background_tasks: BackgroundTasks):
    if not is_password_strong(password):
        raise HTTPException(status_code=400,
                            detail="Password must be at least 8 characters long, contain a digit, and an uppercase letter.")

    db = SessionLocal()
    user = db.query(User).filter(User.email == email).first()
    if user:
        db.close()
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = get_password_hash(password)
    new_user = User(email=email, hashed_password=hashed_password, role='user')  # 默认角色为用户
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # 发送验证邮件
    background_tasks.add_task(send_verification_email, email, new_user.id)

    db.close()
    return {"message": "User created successfully. Please verify your email."}


@app.post("/login")
async def login(email: str, password: str, request: Request):
    db = SessionLocal()
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        db.close()
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token = encode_auth_token(user.id)
    refresh_token = encode_auth_token(user.id)

    user_agent = request.headers.get("User-Agent")
    login_history = LoginHistory(user_agent=user_agent, user_id=user.id)
    db.add(login_history)

    # 增加登录次数
    user.login_count = (user.login_count or 0) + 1
    db.commit()
    db.close()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user_info": {
            "email": user.email,
            "role": user.role,
            "login_count": user.login_count
        }
    }


@app.post("/refresh")
async def refresh(refresh_token: str):
    user_id = decode_token(refresh_token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    if redis_client.exists(f"invalid_refresh_token:{refresh_token}"):
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    access_token = encode_auth_token(user_id)
    return {"access_token": access_token}


@app.put("/user/update")
async def update_user(email: str, password: str, user_id: int):
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        db.close()
        raise HTTPException(status_code=404, detail="User not found")

    user.email = email
    user.hashed_password = get_password_hash(password)
    db.commit()
    db.close()

    return {"message": "User updated successfully"}


@app.get("/user/history")
async def get_login_history(user_id: int):
    db = SessionLocal()
    history = db.query(LoginHistory).filter(LoginHistory.user_id == user_id).all()
    db.close()
    return [{"user_agent": h.user_agent, "datetime": h.datetime} for h in history]


@app.post("/logout")
async def logout(user_id: int, access_token: str, refresh_token: str):
    redis_client.set(f"invalid_access_token:{access_token}", "invalid", ex=3600)  # 1小时过期
    redis_client.set(f"invalid_refresh_token:{refresh_token}", "invalid", ex=3600)  # 1小时过期

    return {"message": "Logged out successfully"}


def is_token_invalid(token: str) -> bool:
    return redis_client.exists(f"invalid_access_token:{token}") or redis_client.exists(f"invalid_refresh_token:{token}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host='127.0.0.1', port=8080, reload=True, workers=1)
