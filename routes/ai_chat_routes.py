from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from auth.auth import get_current_user
from data.data_manager import DataManager

router = APIRouter()
templates = Jinja2Templates(directory="templates")
data_manager = DataManager()

@router.get("/ai-chat", response_class=HTMLResponse)
async def ai_chat_page(request: Request, current_user: dict = Depends(get_current_user)):
    """Страница чата с ИИ"""
    return templates.TemplateResponse("ai_chat.html", {
        "request": request,
        "user": current_user
    })

@router.get("/ai-chat/history", response_class=HTMLResponse)
async def ai_chat_history(request: Request, current_user: dict = Depends(get_current_user)):
    """История чата с ИИ"""
    # Получаем историю чата пользователя
    chat_history = data_manager.load_json(f"chat_{current_user['username']}", "ai_chat")
    
    return templates.TemplateResponse("ai_chat_history.html", {
        "request": request,
        "user": current_user,
        "chat_history": chat_history or []
    }) 