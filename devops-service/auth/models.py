from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime

class User(BaseModel):
    username: str
    disabled: Optional[bool] = None
    role: Literal["Разработчик", "Сопровожденец", "DevOps"]
    full_name: Optional[str] = None

class UserInDB(User):
    hashed_password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserCreate(BaseModel):
    username: str
    password: str
    role: Literal["Разработчик", "Сопровожденец", "DevOps"]
    full_name: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# Модели для новостей
class NewsCreate(BaseModel):
    title: str
    content: str
    label: str
    author: str

class NewsUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    label: Optional[str] = None

class News(BaseModel):
    id: str
    title: str
    content: str
    label: str
    author: str
    created_at: datetime
    updated_at: Optional[datetime] = None 