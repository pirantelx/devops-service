from fastapi import APIRouter, Request, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from auth.auth import get_current_user_from_request
from data.data_manager import DataManager

router = APIRouter()
templates = Jinja2Templates(
    directory=["./templates/autodeploy", "./templates/main"]
)
data_manager = DataManager()

@router.get("/deployments", response_class=HTMLResponse)
async def deployments_page(request: Request):
    """Страница автономных внедрений"""
    current_user = await get_current_user_from_request(request)
    if not current_user:
        return templates.TemplateResponse("login.html", {"request": request})
    
    deployments_list = data_manager.list_files("deployments")
    deployments_data = []
    for name in deployments_list:
        data = data_manager.load_deployment_data(name)
        if data:
            deployments_data.append({"name": name, "data": data})
    return templates.TemplateResponse("deployments.html", {"request": request, "user": current_user, "deployments_list": deployments_data})

@router.get("/deployments/{name}", response_class=HTMLResponse)
async def deployment_detail(request: Request, name: str):
    current_user = await get_current_user_from_request(request)
    if not current_user:
        return templates.TemplateResponse("login.html", {"request": request})
    
    data = data_manager.load_deployment_data(name)
    return templates.TemplateResponse("deployment_detail.html", {"request": request, "user": current_user, "deployment": data, "name": name})

@router.get("/deployments/create", response_class=HTMLResponse)
async def deployment_create_page(request: Request):
    """Страница создания нового внедрения"""
    current_user = await get_current_user_from_request(request)
    if not current_user:
        return templates.TemplateResponse("login.html", {"request": request})
    
    return templates.TemplateResponse("deployment_create.html", {
        "request": request,
        "user": current_user
    }) 