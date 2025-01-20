import jwt
from passlib.context import CryptContext
from fastapi import HTTPException
from datetime import datetime, timedelta


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
secret = "your_secret_key"

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def encode_auth_token(user_id: int) -> str:
    payload = {
        'exp': datetime.utcnow() + timedelta(minutes=5),
        'iat': datetime.utcnow(),
        'sub': user_id
    }
    return jwt.encode(payload, secret, algorithm='HS256')

def decode_token(token: str) -> int:
    try:
        payload = jwt.decode(token, secret, algorithms=['HS256'])
        return payload['sub']
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail='Token expired')
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail='Invalid token')