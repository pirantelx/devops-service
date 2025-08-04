from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from auth.auth import get_current_user_from_request

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    """Главная страница"""
    current_user = await get_current_user_from_request(request)
    return templates.TemplateResponse("home.html", {"request": request, "user": current_user})

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    """Страница дашборда"""
    current_user = await get_current_user_from_request(request)
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": current_user}) 