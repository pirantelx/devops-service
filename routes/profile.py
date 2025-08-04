from fastapi import APIRouter, Request, HTTPException, status, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from auth.auth import get_current_user_from_request

router = APIRouter()
templates = Jinja2Templates(directory="templates/auth")

@router.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request):
    """Страница профиля"""
    current_user = await get_current_user_from_request(request)
    if not current_user:
        return templates.TemplateResponse("login.html", {"request": request})
    
    return templates.TemplateResponse("profile.html", {"request": request, "user": current_user})

@router.get("/profile/edit", response_class=HTMLResponse)
async def profile_edit_page(request: Request, current_user: dict = Depends(get_current_user_from_request)):
    """Страница редактирования профиля"""
    return templates.TemplateResponse("profile_edit.html", {
        "request": request,
        "user": current_user
    }) 