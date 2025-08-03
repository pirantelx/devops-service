from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/home", response_class=HTMLResponse)
async def home_page(request: Request):
    """Главная страница"""
    return templates.TemplateResponse("home.html", {"request": request})

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Дашборд"""
    return templates.TemplateResponse("dashboard.html", {"request": request}) 