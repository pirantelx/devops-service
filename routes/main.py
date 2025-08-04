from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from auth.auth import get_current_user_from_request

router = APIRouter()
templates = Jinja2Templates(directory="templates/main")

@router.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    """Главная страница"""
    current_user = await get_current_user_from_request(request)
    return templates.TemplateResponse("index.html", {"request": request, "user": current_user})