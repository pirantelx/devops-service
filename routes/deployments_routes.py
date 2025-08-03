from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from auth.auth import get_current_user
from data.data_manager import DataManager

router = APIRouter()
templates = Jinja2Templates(directory="templates")
data_manager = DataManager()

@router.get("/deployments", response_class=HTMLResponse)
async def deployments_page(request: Request, current_user: dict = Depends(get_current_user)):
    """Страница автономных внедрений"""
    # Получаем список всех внедрений
    deployments_list = data_manager.list_files("deployments")
    deployments_data = []
    
    for name in deployments_list:
        data = data_manager.load_deployment(name)
        if data:
            deployments_data.append({"name": name, "data": data})
    
    return templates.TemplateResponse("deployments.html", {
        "request": request,
        "user": current_user,
        "deployments_list": deployments_data
    })

@router.get("/deployments/{name}", response_class=HTMLResponse)
async def deployment_detail(request: Request, name: str, current_user: dict = Depends(get_current_user)):
    """Детальная страница внедрения"""
    data = data_manager.load_deployment(name)
    if not data:
        return templates.TemplateResponse("404.html", {"request": request})
    
    return templates.TemplateResponse("deployment_detail.html", {
        "request": request,
        "user": current_user,
        "name": name,
        "data": data
    })

@router.get("/deployments/create", response_class=HTMLResponse)
async def deployment_create_page(request: Request, current_user: dict = Depends(get_current_user)):
    """Страница создания нового внедрения"""
    return templates.TemplateResponse("deployment_create.html", {
        "request": request,
        "user": current_user
    }) 