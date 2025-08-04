from fastapi import APIRouter, Request, HTTPException, status, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from auth.auth import get_current_user_from_request
from auth.permissions import can_manage_news, can_view_news, can_edit_news, can_delete_news
from data.news_manager import NewsManager
from auth.models import NewsCreate, NewsUpdate
from typing import Optional

router = APIRouter()
templates = Jinja2Templates(
    directory=["./templates/news", "./templates/main"]
)
news_manager = NewsManager()

@router.get("/news", response_class=HTMLResponse)
async def news_page(
    request: Request,
    page: int = Query(1, ge=1),
    search: Optional[str] = Query(None),
    label: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None)
):
    """Страница новостей с фильтрацией и пагинацией"""
    current_user = await get_current_user_from_request(request)
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    
    # Проверяем права на просмотр новостей
    if not can_view_news(current_user):
        raise HTTPException(status_code=403, detail="Недостаточно прав для просмотра новостей")
    
    # Получаем новости с фильтрацией и пагинацией
    result = news_manager.get_all_news(
        page=page,
        per_page=6,  # 6 новостей на страницу
        search=search,
        label_filter=label,
        date_from=date_from,
        date_to=date_to
    )
    
    # Получаем список всех лейблов для фильтра
    labels = news_manager.get_labels()
    
    return templates.TemplateResponse("news.html", {
        "request": request,
        "user": current_user,
        "news_list": result["news"],
        "pagination": {
            "page": result["page"],
            "pages": result["pages"],
            "has_prev": result["has_prev"],
            "has_next": result["has_next"],
            "total": result["total"]
        },
        "filters": {
            "search": search,
            "label": label,
            "date_from": date_from,
            "date_to": date_to
        },
        "labels": labels,
        "can_manage_news": can_manage_news(current_user)
    })


@router.get("/news/create", response_class=HTMLResponse)
async def news_create_page(request: Request):
    """Страница создания новости"""
    current_user = await get_current_user_from_request(request)
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    
    # Проверяем права на создание новостей
    if not can_manage_news(current_user):
        raise HTTPException(status_code=403, detail="Недостаточно прав для создания новостей")
    
    labels = news_manager.get_labels()
    
    return templates.TemplateResponse("news_create.html", {
        "request": request,
        "user": current_user,
        "labels": labels
    })

@router.post("/news/create")
async def create_news(
    request: Request,
    title: str = Form(...),
    content: str = Form(...),
    label: str = Form(...)
):
    """API для создания новости"""
    current_user = await get_current_user_from_request(request)
    if not current_user:
        raise HTTPException(status_code=401, detail="Необходима авторизация")
    
    # Проверяем права на создание новостей
    if not can_manage_news(current_user):
        raise HTTPException(status_code=403, detail="Недостаточно прав для создания новостей")
    
    news_data = NewsCreate(
        title=title,
        content=content,
        label=label,
        author=current_user["username"]
    )
    
    news = news_manager.create_news(news_data)
    
    return RedirectResponse(url=f"/news/{news.id}", status_code=302)

@router.get("/news/{news_id}", response_class=HTMLResponse)
async def news_detail(request: Request, news_id: str):
    """Детальная страница новости"""
    current_user = await get_current_user_from_request(request)
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    
    news = news_manager.get_news(news_id)
    if not news:
        raise HTTPException(status_code=404, detail="Новость не найдена")
    
    return templates.TemplateResponse("news_detail.html", {
        "request": request,
        "user": current_user,
        "news": news
    })

@router.get("/news/{news_id}/edit", response_class=HTMLResponse)
async def news_edit_page(request: Request, news_id: str):
    """Страница редактирования новости"""
    current_user = await get_current_user_from_request(request)
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    
    news = news_manager.get_news(news_id)
    if not news:
        raise HTTPException(status_code=404, detail="Новость не найдена")
    
    # Проверяем права на редактирование новости
    if not can_edit_news(current_user, news.author):
        raise HTTPException(status_code=403, detail="Недостаточно прав для редактирования новости")
    
    labels = news_manager.get_labels()
    
    return templates.TemplateResponse("news_edit.html", {
        "request": request,
        "user": current_user,
        "news": news,
        "labels": labels
    })

@router.post("/news/{news_id}/edit")
async def edit_news(
    request: Request,
    news_id: str,
    title: str = Form(...),
    content: str = Form(...),
    label: str = Form(...)
):
    """API для редактирования новости"""
    current_user = await get_current_user_from_request(request)
    if not current_user:
        raise HTTPException(status_code=401, detail="Необходима авторизация")
    
    news = news_manager.get_news(news_id)
    if not news:
        raise HTTPException(status_code=404, detail="Новость не найдена")
    
    # Проверяем права на редактирование новости
    if not can_edit_news(current_user, news.author):
        raise HTTPException(status_code=403, detail="Недостаточно прав для редактирования новости")
    
    news_data = NewsUpdate(
        title=title,
        content=content,
        label=label
    )
    
    updated_news = news_manager.update_news(news_id, news_data)
    if not updated_news:
        raise HTTPException(status_code=404, detail="Новость не найдена")
    
    return RedirectResponse(url=f"/news/{updated_news.id}", status_code=302)

@router.post("/news/{news_id}/delete")
async def delete_news(request: Request, news_id: str):
    """API для удаления новости"""
    current_user = await get_current_user_from_request(request)
    if not current_user:
        raise HTTPException(status_code=401, detail="Необходима авторизация")
    
    news = news_manager.get_news(news_id)
    if not news:
        raise HTTPException(status_code=404, detail="Новость не найдена")
    
    # Проверяем права на удаление новости
    if not can_delete_news(current_user, news.author):
        raise HTTPException(status_code=403, detail="Недостаточно прав для удаления новости")
    
    success = news_manager.delete_news(news_id)
    if not success:
        raise HTTPException(status_code=404, detail="Новость не найдена")
    
    return RedirectResponse(url="/news", status_code=302) 