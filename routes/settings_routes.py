from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from auth.auth import get_current_user
from data.data_manager import DataManager

router = APIRouter()
templates = Jinja2Templates(directory="templates")
data_manager = DataManager()

@router.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request, current_user: dict = Depends(get_current_user)):
    """Страница проверки настроек"""
    # Получаем список всех настроек
    settings_list = data_manager.list_files("settings")
    settings_data = []
    
    for name in settings_list:
        data = data_manager.load_settings(name)
        if data:
            settings_data.append({"name": name, "data": data})
    
    return templates.TemplateResponse("settings.html", {
        "request": request,
        "user": current_user,
        "settings_list": settings_data
    })

@router.get("/settings/{name}", response_class=HTMLResponse)
async def settings_detail(request: Request, name: str, current_user: dict = Depends(get_current_user)):
    """Детальная страница настроек"""
    data = data_manager.load_settings(name)
    if not data:
        return templates.TemplateResponse("404.html", {"request": request})
    
    return templates.TemplateResponse("settings_detail.html", {
        "request": request,
        "user": current_user,
        "settings": data,
        "name": name
    })

@router.get("/settings/create", response_class=HTMLResponse)
async def settings_create_page(request: Request, current_user: dict = Depends(get_current_user)):
    """Страница создания новых настроек"""
    return templates.TemplateResponse("settings_create.html", {
        "request": request,
        "user": current_user
    }) 