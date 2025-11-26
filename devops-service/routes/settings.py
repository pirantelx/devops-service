from fastapi import APIRouter, Request, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from auth.auth import get_current_user_from_request
from data.data_manager import DataManager

router = APIRouter()
templates = Jinja2Templates(
    directory=["./templates/check-settings", "./templates/main"]
)
data_manager = DataManager()

@router.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    """Страница проверки настроек"""
    current_user = await get_current_user_from_request(request)
    if not current_user:
        return templates.TemplateResponse("login.html", {"request": request})
    
    settings_list = data_manager.list_files("settings")
    settings_data = []
    for name in settings_list:
        data = data_manager.load_settings_data(name)
        if data:
            settings_data.append({"name": name, "data": data})
    return templates.TemplateResponse("settings.html", {"request": request, "user": current_user, "settings_list": settings_data})

@router.get("/settings/{name}", response_class=HTMLResponse)
async def settings_detail(request: Request, name: str):
    current_user = await get_current_user_from_request(request)
    if not current_user:
        return templates.TemplateResponse("login.html", {"request": request})
    
    data = data_manager.load_settings_data(name)
    return templates.TemplateResponse("settings_detail.html", {"request": request, "user": current_user, "settings": data, "name": name})

@router.get("/settings/create", response_class=HTMLResponse)
async def settings_create_page(request: Request):
    """Страница создания новых настроек"""
    current_user = await get_current_user_from_request(request)
    if not current_user:
        return templates.TemplateResponse("login.html", {"request": request})
    
    return templates.TemplateResponse("settings_create.html", {
        "request": request,
        "user": current_user
    }) 