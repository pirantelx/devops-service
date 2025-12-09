from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from auth.auth import get_current_user_from_request

router = APIRouter()
templates = Jinja2Templates(directory="templates/main")
ai_chat_templates = Jinja2Templates(directory=["./templates/ai-chat", "./templates/main"])

@router.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    """Главная страница - чат с ИИ"""
    current_user = await get_current_user_from_request(request)
    if not current_user:
        return templates.TemplateResponse("login.html", {"request": request})
    
    return ai_chat_templates.TemplateResponse("ai_chat.html", {"request": request, "user": current_user})