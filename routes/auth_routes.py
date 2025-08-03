from fastapi import APIRouter, Request, HTTPException, status, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBearer
from auth.models import UserLogin, UserCreate, Token
from auth.auth import authenticate_user, get_current_user, create_access_token
from auth.utils import get_password_hash, load_users, save_users
import json

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Страница входа"""
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """Страница регистрации"""
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/login")
async def login(user_credentials: UserLogin):
    """API для входа пользователя"""
    user = await authenticate_user(user_credentials.username, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}

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
        "email": user_data.email,
        "full_name": user_data.full_name,
        "hashed_password": hashed_password,
        "disabled": False
    }
    
    users[user_data.username] = user_dict
    save_users(users)
    
    return {"message": "User created successfully"}

@router.get("/logout")
async def logout():
    """Выход из системы"""
    return RedirectResponse(url="/login")

@router.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request, current_user: dict = Depends(get_current_user)):
    """Страница профиля"""
    return templates.TemplateResponse("profile.html", {"request": request, "user": current_user}) 