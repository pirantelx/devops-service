from fastapi import APIRouter, Request, HTTPException, status, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBearer
from auth.models import UserLogin, UserCreate, Token
from auth.auth import authenticate_user, get_current_user, create_access_token, get_current_user_from_request
from auth.utils import get_password_hash, load_users, save_users
import json

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Страница входа"""
    return templates.TemplateResponse("login/login.html", {"request": request})

@router.post("/login")
async def login(request: Request, user_credentials: UserLogin):
    """API для входа пользователя"""
    user = await authenticate_user(user_credentials.username, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user["username"]})
    
    # Создаем ответ с cookie
    response = RedirectResponse(url="/", status_code=302)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=86400,  # 24 часа
        samesite="lax"
    )
    
    return response

@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """Страница регистрации"""
    return templates.TemplateResponse("login/register.html", {"request": request})

@router.post("/register")
async def register(user_data: UserCreate):
    """API для регистрации пользователя"""
    users = load_users()
    
    if user_data.username in users:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    hashed_password = get_password_hash(user_data.password)
    user_dict = {
        "username": user_data.username,
        "hashed_password": hashed_password,
        "disabled": False,
        "role": user_data.role
    }
    
    users[user_data.username] = user_dict
    save_users(users)
    
    return {"message": "User created successfully"}

@router.get("/logout")
async def logout():
    """Выход из системы"""
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie("access_token")
    return response