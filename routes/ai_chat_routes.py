from fastapi import APIRouter, Request, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from auth.auth import get_current_user_from_request
from data.data_manager import DataManager

router = APIRouter()
templates = Jinja2Templates(directory="templates")
data_manager = DataManager()

@router.get("/ai-chat", response_class=HTMLResponse)
async def ai_chat_page(request: Request):
    """Страница чата с ИИ"""
    current_user = await get_current_user_from_request(request)
    if not current_user:
        return templates.TemplateResponse("login.html", {"request": request})
    
    return templates.TemplateResponse("ai_chat.html", {"request": request, "user": current_user})

@router.get("/ai-chat/history", response_class=HTMLResponse)
async def ai_chat_history(request: Request):
    """История чата с ИИ"""
    current_user = await get_current_user_from_request(request)
    if not current_user:
        return templates.TemplateResponse("login.html", {"request": request})
    
    # Здесь можно загрузить историю чата из data_manager
    chat_history = data_manager.load_chat_history(current_user["username"])
    return templates.TemplateResponse("ai_chat_history.html", {"request": request, "user": current_user, "chat_history": chat_history}) 