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
from data.news_manager import NewsManager
from routes import (
    main,
    auth,
    as_fp,
    settings,
    deployments,
    infrastructure,
    ai_chat,
    profile,
    news,
    problems
    )

app = FastAPI(title="DevOps Service Portal", version="1.0.0")

templates = Jinja2Templates(directory="templates")

# Инициализация менеджера данных
data_manager = DataManager()
news_manager = NewsManager()

# Подключение роутов
app.include_router(main.router)
app.include_router(auth.router)
app.include_router(as_fp.router)
app.include_router(settings.router)
app.include_router(deployments.router)
app.include_router(infrastructure.router)
app.include_router(ai_chat.router)
app.include_router(profile.router)
app.include_router(news.router)
app.include_router(problems.router)


if __name__ == "__main__":
    os.system ("ls -l")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
