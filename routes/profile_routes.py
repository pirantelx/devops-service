from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from auth.auth import get_current_user

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request, current_user: dict = Depends(get_current_user)):
    """Страница профиля пользователя"""
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "user": current_user
    })

@router.get("/profile/edit", response_class=HTMLResponse)
async def profile_edit_page(request: Request, current_user: dict = Depends(get_current_user)):
    """Страница редактирования профиля"""
    return templates.TemplateResponse("profile_edit.html", {
        "request": request,
        "user": current_user
    }) 