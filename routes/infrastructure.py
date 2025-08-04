from fastapi import APIRouter, Request, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from auth.auth import get_current_user_from_request
from data.data_manager import DataManager

router = APIRouter()
templates = Jinja2Templates(directory="templates")
data_manager = DataManager()

@router.get("/infrastructure", response_class=HTMLResponse)
async def infrastructure_page(request: Request):
    """Страница инфраструктурных работ"""
    current_user = await get_current_user_from_request(request)
    if not current_user:
        return templates.TemplateResponse("login.html", {"request": request})
    
    infrastructure_list = data_manager.list_files("infrastructure")
    infrastructure_data = []
    for name in infrastructure_list:
        data = data_manager.load_infrastructure_data(name)
        if data:
            infrastructure_data.append({"name": name, "data": data})
    return templates.TemplateResponse("infrastructure.html", {"request": request, "user": current_user, "infrastructure_list": infrastructure_data})

@router.get("/infrastructure/{name}", response_class=HTMLResponse)
async def infrastructure_detail(request: Request, name: str):
    current_user = await get_current_user_from_request(request)
    if not current_user:
        return templates.TemplateResponse("login.html", {"request": request})
    
    data = data_manager.load_infrastructure_data(name)
    return templates.TemplateResponse("infrastructure_detail.html", {"request": request, "user": current_user, "infrastructure": data, "name": name})

@router.get("/infrastructure/create", response_class=HTMLResponse)
async def infrastructure_create_page(request: Request):
    """Страница создания новой инфраструктурной работы"""
    current_user = await get_current_user_from_request(request)
    if not current_user:
        return templates.TemplateResponse("login.html", {"request": request})
    
    return templates.TemplateResponse("infrastructure_create.html", {
        "request": request,
        "user": current_user
    }) 