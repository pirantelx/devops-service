from pydantic import BaseModel
from typing import Optional, Literal

class User(BaseModel):
    username: str
    disabled: Optional[bool] = None
    role: Literal["Разработчик", "Сопровожденец", "DevOps"]

class UserInDB(User):
    hashed_password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserCreate(BaseModel):
    username: str
    password: str
    role: Literal["Разработчик", "Сопровожденец", "DevOps"]

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None 