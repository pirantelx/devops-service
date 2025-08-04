from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from auth.utils import verify_password, get_user, verify_token
from auth.models import User

security = HTTPBearer()

async def authenticate_user(username: str, password: str):
    """Аутентификация пользователя"""
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user["hashed_password"]):
        return False
    return user

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Получение текущего пользователя из токена"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    username = verify_token(credentials.credentials)
    if username is None:
        raise credentials_exception
    
    user = get_user(username)
    if user is None:
        raise credentials_exception
    
    return user

async def get_current_user_from_request(request: Request):
    """Получение текущего пользователя из заголовка Authorization или cookie"""
    # Проверяем заголовок Authorization
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        username = verify_token(token)
        if username:
            user = get_user(username)
            if user:
                return user
    
    # Проверяем cookie
    token = request.cookies.get("access_token")
    if token:
        username = verify_token(token)
        if username:
            user = get_user(username)
            if user:
                return user
    
    return None

def create_access_token(data: dict):
    """Создание токена доступа"""
    from auth.utils import create_access_token as create_token
    from datetime import timedelta
    
    access_token_expires = timedelta(minutes=60)
    return create_token(data=data, expires_delta=access_token_expires) 