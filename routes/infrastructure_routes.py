from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from auth.auth import get_current_user
from data.data_manager import DataManager

router = APIRouter()
templates = Jinja2Templates(directory="templates")
data_manager = DataManager()

@router.get("/infrastructure", response_class=HTMLResponse)
async def infrastructure_page(request: Request, current_user: dict = Depends(get_current_user)):
    """Страница инфраструктурных работ"""
    # Получаем список всех инфраструктурных работ
    infrastructure_list = data_manager.list_files("infrastructure")
    infrastructure_data = []
    
    for name in infrastructure_list:
        data = data_manager.load_infrastructure(name)
        if data:
            infrastructure_data.append({"name": name, "data": data})
    
    return templates.TemplateResponse("infrastructure.html", {
        "request": request,
        "user": current_user,
        "infrastructure_list": infrastructure_data
    })

@router.get("/infrastructure/{name}", response_class=HTMLResponse)
async def infrastructure_detail(request: Request, name: str, current_user: dict = Depends(get_current_user)):
    """Детальная страница инфраструктурной работы"""
    data = data_manager.load_infrastructure(name)
    if not data:
        return templates.TemplateResponse("404.html", {"request": request})
    
    return templates.TemplateResponse("infrastructure_detail.html", {
        "request": request,
        "user": current_user,
        "name": name,
        "data": data
    })

@router.get("/infrastructure/create", response_class=HTMLResponse)
async def infrastructure_create_page(request: Request, current_user: dict = Depends(get_current_user)):
    """Страница создания новой инфраструктурной работы"""
    return templates.TemplateResponse("infrastructure_create.html", {
        "request": request,
        "user": current_user
    }) 