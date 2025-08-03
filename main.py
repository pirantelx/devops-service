from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import HTTPBearer
import uvicorn
import os
from pathlib import Path

from auth.auth import get_current_user, create_access_token
from auth.models import User, UserLogin
from auth.utils import verify_password, get_password_hash
from data.data_manager import DataManager
from routes import (
    main_routes,
    auth_routes,
    as_fp_routes,
    settings_routes,
    deployments_routes,
    infrastructure_routes,
    ai_chat_routes,
    profile_routes
)

app = FastAPI(title="DevOps Service Portal", version="1.0.0")

# Настройка статических файлов и шаблонов
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Инициализация менеджера данных
data_manager = DataManager()

# Подключение роутов
app.include_router(main_routes.router)
app.include_router(auth_routes.router)
app.include_router(as_fp_routes.router)
app.include_router(settings_routes.router)
app.include_router(deployments_routes.router)
app.include_router(infrastructure_routes.router)
app.include_router(ai_chat_routes.router)
app.include_router(profile_routes.router)

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Главная страница"""
    return templates.TemplateResponse("index.html", {"request": request})

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 