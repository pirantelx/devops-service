from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import json
import os
from typing import Optional

# Настройки для JWT
SECRET_KEY = "your-secret-key-here"  # В продакшене использовать переменную окружения
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 часа

# Настройки для хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля"""
    try:
        result = pwd_context.verify(plain_password, hashed_password)
        return result
    except Exception as e:
        return False

def get_password_hash(password: str) -> str:
    """Хеширование пароля"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Создание JWT токена"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[str]:
    """Проверка JWT токена"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        return username
    except JWTError:
        return None

def load_users() -> dict:
    """Загрузка пользователей из JSON файла"""
    users_file = "data/users/users.json"
    if os.path.exists(users_file):
        with open(users_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_users(users: dict):
    """Сохранение пользователей в JSON файл"""
    os.makedirs("data", exist_ok=True)
    with open("data/users/users.json", "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

def get_user(username: str):
    """Получение пользователя по имени"""
    users = load_users()
    if username in users:
        user_dict = users[username]
        return user_dict
    return None 