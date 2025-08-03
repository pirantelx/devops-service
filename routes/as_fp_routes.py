from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from auth.auth import get_current_user
from data.data_manager import DataManager

router = APIRouter()
templates = Jinja2Templates(directory="templates")
data_manager = DataManager()

@router.get("/as-fp", response_class=HTMLResponse)
async def as_fp_page(request: Request, current_user: dict = Depends(get_current_user)):
    """Страница сведений о АС/ФП"""
    # Получаем список всех АС/ФП
    as_fp_list = data_manager.list_files("as_fp")
    as_fp_data = []
    
    for name in as_fp_list:
        data = data_manager.load_as_fp_data(name)
        if data:
            as_fp_data.append({"name": name, "data": data})
    
    return templates.TemplateResponse("as_fp.html", {
        "request": request, 
        "user": current_user,
        "as_fp_list": as_fp_data
    })

@router.get("/as-fp/{name}", response_class=HTMLResponse)
async def as_fp_detail(request: Request, name: str, current_user: dict = Depends(get_current_user)):
    """Детальная страница АС/ФП"""
    data = data_manager.load_as_fp_data(name)
    if not data:
        return templates.TemplateResponse("404.html", {"request": request})
    
    return templates.TemplateResponse("as_fp_detail.html", {
        "request": request,
        "user": current_user,
        "name": name,
        "data": data
    })

@router.get("/as-fp/create", response_class=HTMLResponse)
async def as_fp_create_page(request: Request, current_user: dict = Depends(get_current_user)):
    """Страница создания нового АС/ФП"""
    return templates.TemplateResponse("as_fp_create.html", {
        "request": request,
        "user": current_user
    }) 