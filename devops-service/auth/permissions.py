from typing import Optional
from auth.models import User

def can_manage_news(user: Optional[dict]) -> bool:
    """
    Проверяет, может ли пользователь управлять новостями (создавать, редактировать, удалять)
    """
    if not user:
        return False
    
    # Только DevOps могут управлять новостями
    return user.get("role") == "DevOps"

def can_view_news(user: Optional[dict]) -> bool:
    """
    Проверяет, может ли пользователь просматривать новости
    """
    if not user:
        return False
    
    # Все авторизованные пользователи могут просматривать новости
    return True

def can_edit_news(user: Optional[dict], news_author: str) -> bool:
    """
    Проверяет, может ли пользователь редактировать конкретную новость
    """
    if not user:
        return False
    
    # DevOps могут редактировать любые новости
    if can_manage_news(user):
        return True
    
    # Автор новости может редактировать свою новость
    return user.get("username") == news_author

def can_delete_news(user: Optional[dict], news_author: str) -> bool:
    """
    Проверяет, может ли пользователь удалять конкретную новость
    """
    if not user:
        return False
    
    # DevOps могут удалять любые новости
    if can_manage_news(user):
        return True
    
    # Автор новости может удалять свою новость
    return user.get("username") == news_author 