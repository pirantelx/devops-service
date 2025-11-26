import json
import os
from datetime import datetime
from typing import List, Optional, Dict, Any
from auth.models import News, NewsCreate, NewsUpdate
import uuid

class NewsManager:
    def __init__(self, data_dir: str = "data/news"):
        self.data_dir = data_dir
        self.news_file = os.path.join(data_dir, "news.json")
        self._ensure_data_dir()
        self._ensure_news_file()
    
    def _ensure_data_dir(self):
        """Создает директорию для данных, если она не существует"""
        os.makedirs(self.data_dir, exist_ok=True)
    
    def _ensure_news_file(self):
        """Создает файл новостей, если он не существует"""
        if not os.path.exists(self.news_file):
            self._save_news({})
    
    def _load_news(self) -> Dict[str, Any]:
        """Загружает все новости из файла"""
        try:
            with open(self.news_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_news(self, news_data: Dict[str, Any]):
        """Сохраняет новости в файл"""
        with open(self.news_file, 'w', encoding='utf-8') as f:
            json.dump(news_data, f, ensure_ascii=False, indent=2, default=str)
    
    def create_news(self, news_data: NewsCreate) -> News:
        """Создает новую новость"""
        news_id = str(uuid.uuid4())
        now = datetime.now()
        
        news = News(
            id=news_id,
            title=news_data.title,
            content=news_data.content,
            label=news_data.label,
            author=news_data.author,
            created_at=now,
            updated_at=None
        )
        
        # Загружаем существующие новости
        all_news = self._load_news()
        
        # Добавляем новую новость
        all_news[news_id] = news.model_dump()
        
        # Сохраняем обратно
        self._save_news(all_news)
        
        return news
    
    def get_news(self, news_id: str) -> Optional[News]:
        """Получает новость по ID"""
        all_news = self._load_news()
        if news_id in all_news:
            news_data = all_news[news_id]
            # Преобразуем строки дат обратно в datetime
            if isinstance(news_data.get('created_at'), str):
                news_data['created_at'] = datetime.fromisoformat(news_data['created_at'].replace('Z', '+00:00'))
            if news_data.get('updated_at') and isinstance(news_data['updated_at'], str):
                news_data['updated_at'] = datetime.fromisoformat(news_data['updated_at'].replace('Z', '+00:00'))
            return News(**news_data)
        return None
    
    def get_all_news(self, 
                     page: int = 1, 
                     per_page: int = 10, 
                     search: Optional[str] = None,
                     label_filter: Optional[str] = None,
                     date_from: Optional[str] = None,
                     date_to: Optional[str] = None) -> Dict[str, Any]:
        """Получает все новости с пагинацией и фильтрацией"""
        all_news = self._load_news()
        
        # Преобразуем в список News объектов
        news_list = []
        for news_id, news_data in all_news.items():
            # Преобразуем строки дат обратно в datetime
            if isinstance(news_data.get('created_at'), str):
                news_data['created_at'] = datetime.fromisoformat(news_data['created_at'].replace('Z', '+00:00'))
            if news_data.get('updated_at') and isinstance(news_data['updated_at'], str):
                news_data['updated_at'] = datetime.fromisoformat(news_data['updated_at'].replace('Z', '+00:00'))
            news_list.append(News(**news_data))
        
        # Фильтрация
        if search:
            search_lower = search.lower()
            news_list = [news for news in news_list 
                        if search_lower in news.title.lower() 
                        or search_lower in news.content.lower()]
        
        if label_filter:
            news_list = [news for news in news_list if news.label == label_filter]
        
        if date_from:
            try:
                date_from_dt = datetime.fromisoformat(date_from)
                news_list = [news for news in news_list if news.created_at >= date_from_dt]
            except ValueError:
                pass
        
        if date_to:
            try:
                date_to_dt = datetime.fromisoformat(date_to)
                news_list = [news for news in news_list if news.created_at <= date_to_dt]
            except ValueError:
                pass
        
        # Сортировка по дате создания (новые сначала)
        news_list.sort(key=lambda x: x.created_at, reverse=True)
        
        # Пагинация
        total = len(news_list)
        start = (page - 1) * per_page
        end = start + per_page
        paginated_news = news_list[start:end]
        
        return {
            "news": paginated_news,
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": (total + per_page - 1) // per_page,
            "has_prev": page > 1,
            "has_next": end < total
        }
    
    def update_news(self, news_id: str, news_data: NewsUpdate) -> Optional[News]:
        """Обновляет новость"""
        all_news = self._load_news()
        if news_id not in all_news:
            return None
        
        # Загружаем существующую новость
        existing_news = self.get_news(news_id)
        if not existing_news:
            return None
        
        # Обновляем поля
        update_data = news_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(existing_news, field, value)
        
        # Обновляем время изменения
        existing_news.updated_at = datetime.now()
        
        # Сохраняем обратно
        all_news[news_id] = existing_news.model_dump()
        self._save_news(all_news)
        
        return existing_news
    
    def delete_news(self, news_id: str) -> bool:
        """Удаляет новость"""
        all_news = self._load_news()
        if news_id in all_news:
            del all_news[news_id]
            self._save_news(all_news)
            return True
        return False
    
    def get_labels(self) -> List[str]:
        """Получает список всех уникальных лейблов"""
        all_news = self._load_news()
        labels = set()
        for news_data in all_news.values():
            if 'label' in news_data:
                labels.add(news_data['label'])
        return sorted(list(labels)) 