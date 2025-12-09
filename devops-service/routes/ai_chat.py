from fastapi import APIRouter, Request, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Optional
from auth.auth import get_current_user_from_request
from data.data_manager import DataManager
from services.llm_service import LLMService

router = APIRouter()

templates = Jinja2Templates(
    directory=["./templates/ai-chat", "./templates/main"]
)

data_manager = DataManager()
llm_service = LLMService()

class ChatMessage(BaseModel):
    message: str

class ChatHistoryResponse(BaseModel):
    messages: List[dict]

@router.get("/ai-chat", response_class=HTMLResponse)
async def ai_chat_page(request: Request):
    """Страница чата с ИИ"""
    current_user = await get_current_user_from_request(request)
    if not current_user:
        return templates.TemplateResponse("login.html", {"request": request})
    
    return templates.TemplateResponse("ai_chat.html", {"request": request, "user": current_user})

@router.post("/ai-chat/message")
async def ai_chat_message(request: Request, chat_message: ChatMessage):
    """API endpoint для отправки сообщения в чат"""
    current_user = await get_current_user_from_request(request)
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Необходима авторизация"
        )
    
    username = current_user["username"]
    user_message = chat_message.message
    
    # Сохраняем сообщение пользователя
    data_manager.add_chat_message(username, "user", user_message)
    
    # Загружаем историю чата
    chat_history = data_manager.load_chat_history(username)
    
    # Формируем историю для LLM
    history_for_llm = [
        {"role": msg["role"], "content": msg["content"]}
        for msg in chat_history[-10:]  # Последние 10 сообщений
    ]
    
    # Генерируем ответ
    try:
        ai_response = await llm_service.generate_response(user_message, history_for_llm)
        
        # Сохраняем ответ ИИ
        data_manager.add_chat_message(username, "assistant", ai_response)
        
        return JSONResponse({
            "response": ai_response,
            "status": "success"
        })
    except Exception as e:
        error_message = f"Ошибка при генерации ответа: {str(e)}"
        return JSONResponse(
            {"response": error_message, "status": "error"},
            status_code=500
        )

@router.get("/ai-chat/history", response_class=HTMLResponse)
async def ai_chat_history(request: Request):
    """История чата с ИИ"""
    current_user = await get_current_user_from_request(request)
    if not current_user:
        return templates.TemplateResponse("login.html", {"request": request})
    
    chat_history = data_manager.load_chat_history(current_user["username"])
    return templates.TemplateResponse("ai_chat_history.html", {"request": request, "user": current_user, "chat_history": chat_history})

@router.get("/ai-chat/history/api")
async def ai_chat_history_api(request: Request):
    """API endpoint для получения истории чата"""
    current_user = await get_current_user_from_request(request)
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Необходима авторизация"
        )
    
    chat_history = data_manager.load_chat_history(current_user["username"])
    return JSONResponse({"messages": chat_history}) 