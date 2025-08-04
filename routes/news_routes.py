from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from auth.auth import get_current_user
from data.data_manager import DataManager
import json

router = APIRouter()
templates = Jinja2Templates(directory="templates")
data_manager = DataManager()

@router.get("/news", response_class=HTMLResponse)
async def news_page(request: Request, current_user: dict = Depends(get_current_user)):
    """Страница новостей"""
    try:
        news_data = data_manager.load_news_data()
    except FileNotFoundError:
        news_data = []
    
    return templates.TemplateResponse("news.html", {
        "request": request, 
        "user": current_user,
        "news": news_data
    })

@router.get("/news/{news_id}", response_class=HTMLResponse)
async def news_detail(request: Request, news_id: str, current_user: dict = Depends(get_current_user)):
    """Детальная страница новости"""
    try:
        news_data = data_manager.load_news_data()
        news_item = next((item for item in news_data if item.get("id") == news_id), None)
        
        if not news_item:
            raise HTTPException(status_code=404, detail="Новость не найдена")
            
        return templates.TemplateResponse("news_detail.html", {
            "request": request,
            "user": current_user,
            "news": news_item
        })
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Новость не найдена")

@router.get("/news/create", response_class=HTMLResponse)
async def news_create_page(request: Request, current_user: dict = Depends(get_current_user)):
    """Страница создания новости"""
    return templates.TemplateResponse("news_create.html", {
        "request": request,
        "user": current_user
    }) 