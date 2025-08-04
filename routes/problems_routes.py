from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from auth.auth import get_current_user
from data.data_manager import DataManager
import json

router = APIRouter()
templates = Jinja2Templates(directory="templates")
data_manager = DataManager()

@router.get("/problems", response_class=HTMLResponse)
async def problems_page(request: Request, current_user: dict = Depends(get_current_user)):
    """Страница проблем и их решений"""
    try:
        problems_data = data_manager.load_problems_data()
    except FileNotFoundError:
        problems_data = []
    
    return templates.TemplateResponse("problems.html", {
        "request": request, 
        "user": current_user,
        "problems": problems_data
    })

@router.get("/problems/{problem_id}", response_class=HTMLResponse)
async def problem_detail(request: Request, problem_id: str, current_user: dict = Depends(get_current_user)):
    """Детальная страница проблемы"""
    try:
        problems_data = data_manager.load_problems_data()
        problem_item = next((item for item in problems_data if item.get("id") == problem_id), None)
        
        if not problem_item:
            raise HTTPException(status_code=404, detail="Проблема не найдена")
            
        return templates.TemplateResponse("problem_detail.html", {
            "request": request,
            "user": current_user,
            "problem": problem_item
        })
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Проблема не найдена")

@router.get("/problems/create", response_class=HTMLResponse)
async def problem_create_page(request: Request, current_user: dict = Depends(get_current_user)):
    """Страница создания проблемы"""
    return templates.TemplateResponse("problem_create.html", {
        "request": request,
        "user": current_user
    }) 