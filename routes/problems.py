from fastapi import APIRouter, Request, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from auth.auth import get_current_user_from_request
from data.data_manager import DataManager

router = APIRouter()
templates = Jinja2Templates(directory="templates")
data_manager = DataManager()

@router.get("/problems", response_class=HTMLResponse)
async def problems_page(request: Request):
    """Страница проблем и их решений"""
    current_user = await get_current_user_from_request(request)
    if not current_user:
        return templates.TemplateResponse("login.html", {"request": request})
    
    problems_list = data_manager.list_files("problems")
    problems_data = []
    for name in problems_list:
        data = data_manager.load_problems_data(name)
        if data:
            problems_data.append({"name": name, "data": data})
    return templates.TemplateResponse("problems.html", {"request": request, "user": current_user, "problems_list": problems_data})

@router.get("/problems/{problem_id}", response_class=HTMLResponse)
async def problem_detail(request: Request, problem_id: str):
    current_user = await get_current_user_from_request(request)
    if not current_user:
        return templates.TemplateResponse("login.html", {"request": request})
    
    data = data_manager.load_problems_data(problem_id)
    return templates.TemplateResponse("problem_detail.html", {"request": request, "user": current_user, "problem": data, "problem_id": problem_id})

@router.get("/problems/create", response_class=HTMLResponse)
async def problem_create_page(request: Request):
    """Страница создания проблемы"""
    current_user = await get_current_user_from_request(request)
    if not current_user:
        return templates.TemplateResponse("login.html", {"request": request})
    
    return templates.TemplateResponse("problem_create.html", {
        "request": request,
        "user": current_user
    }) 