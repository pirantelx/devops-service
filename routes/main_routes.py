from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from auth.auth import get_current_user

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def home_page(request: Request, current_user: dict = Depends(get_current_user)):
    """Главная страница"""
    return templates.TemplateResponse("home.html", {"request": request, "user": current_user})

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, current_user: dict = Depends(get_current_user)):
    """Дашборд"""
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": current_user}) 