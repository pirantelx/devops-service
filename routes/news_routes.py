from fastapi import APIRouter, Request, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from auth.auth import get_current_user_from_request
from data.data_manager import DataManager

router = APIRouter()
templates = Jinja2Templates(directory="templates")
data_manager = DataManager()

@router.get("/news", response_class=HTMLResponse)
async def news_page(request: Request):
    """Страница новостей"""
    current_user = await get_current_user_from_request(request)
    if not current_user:
        return templates.TemplateResponse("login.html", {"request": request})
    
    news_list = data_manager.list_files("news")
    news_data = []
    for name in news_list:
        data = data_manager.load_news_data(name)
        if data:
            news_data.append({"name": name, "data": data})
    return templates.TemplateResponse("news.html", {"request": request, "user": current_user, "news_list": news_data})

@router.get("/news/{news_id}", response_class=HTMLResponse)
async def news_detail(request: Request, news_id: str):
    current_user = await get_current_user_from_request(request)
    if not current_user:
        return templates.TemplateResponse("login.html", {"request": request})
    
    data = data_manager.load_news_data(news_id)
    return templates.TemplateResponse("news_detail.html", {"request": request, "user": current_user, "news": data, "news_id": news_id})

@router.get("/news/create", response_class=HTMLResponse)
async def news_create_page(request: Request):
    """Страница создания новости"""
    current_user = await get_current_user_from_request(request)
    if not current_user:
        return templates.TemplateResponse("login.html", {"request": request})
    
    return templates.TemplateResponse("news_create.html", {
        "request": request,
        "user": current_user
    }) 