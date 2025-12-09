import os
import json
import httpx
from typing import List, Dict, Any, Optional
from pathlib import Path
from data.data_manager import DataManager
from data.news_manager import NewsManager


class LLMService:
    def __init__(self, ollama_host: str = None):
        self.ollama_host = ollama_host or os.getenv("OLLAMA_HOST", "http://localhost:11434")
        # Используем более легкую модель для быстрой работы
        # Можно изменить на другую модель: llama3.2, mistral, qwen2.5 и т.д.
        self.model_name = os.getenv("OLLAMA_MODEL", "llama3.2:1b")
        self.data_manager = DataManager()
        self.news_manager = NewsManager()
        self._model_checked = False
        # Не проверяем модель при инициализации, чтобы не блокировать запуск приложения
    
    def _ensure_model_loaded(self):
        """Проверяет и загружает модель, если необходимо (вызывается при первом использовании)"""
        if self._model_checked:
            return
        
        try:
            response = httpx.get(f"{self.ollama_host}/api/tags", timeout=5.0)
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [m.get("name", "") for m in models]
                if self.model_name not in model_names:
                    print(f"Модель {self.model_name} не найдена. Загружаю...")
                    self._pull_model()
            self._model_checked = True
        except Exception as e:
            print(f"Предупреждение: не удалось подключиться к Ollama: {e}")
            print("Убедитесь, что Ollama запущен и доступен")
            self._model_checked = True  # Помечаем как проверенную, чтобы не повторять попытки
    
    def _pull_model(self):
        """Загружает модель в Ollama"""
        try:
            response = httpx.post(
                f"{self.ollama_host}/api/pull",
                json={"name": self.model_name},
                timeout=300.0  # Загрузка может занять время
            )
            if response.status_code == 200:
                print(f"Модель {self.model_name} успешно загружена")
        except Exception as e:
            print(f"Ошибка загрузки модели: {e}")
    
    def _load_all_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """Загружает все данные системы для индексации"""
        all_data = {
            "news": [],
            "problems": [],
            "deployments": [],
            "infrastructure": [],
            "as_fp": [],
            "settings": []
        }
        
        # Загружаем новости
        try:
            news_data = self.news_manager.get_all_news(page=1, per_page=1000)
            for news in news_data.get("news", []):
                all_data["news"].append({
                    "type": "news",
                    "id": news.id,
                    "title": news.title,
                    "content": news.content,
                    "label": news.label,
                    "author": news.author,
                    "created_at": str(news.created_at)
                })
        except Exception as e:
            print(f"Ошибка загрузки новостей: {e}")
        
        # Загружаем проблемы
        try:
            problems = self.data_manager.load_problems_data("problems")
            if problems:
                for problem in problems:
                    all_data["problems"].append({
                        "type": "problem",
                        "data": problem
                    })
        except Exception as e:
            print(f"Ошибка загрузки проблем: {e}")
        
        # Загружаем внедрения
        try:
            deployment_files = self.data_manager.list_files("deployments")
            for name in deployment_files:
                deployment = self.data_manager.load_deployment(name)
                if deployment:
                    all_data["deployments"].append({
                        "type": "deployment",
                        "name": name,
                        "data": deployment
                    })
        except Exception as e:
            print(f"Ошибка загрузки внедрений: {e}")
        
        # Загружаем инфраструктуру
        try:
            infrastructure_files = self.data_manager.list_files("infrastructure")
            for name in infrastructure_files:
                infra = self.data_manager.load_infrastructure(name)
                if infra:
                    all_data["infrastructure"].append({
                        "type": "infrastructure",
                        "name": name,
                        "data": infra
                    })
        except Exception as e:
            print(f"Ошибка загрузки инфраструктуры: {e}")
        
        # Загружаем АС/ФП
        try:
            as_fp_files = self.data_manager.list_files("as_fp")
            for name in as_fp_files:
                as_fp = self.data_manager.load_as_fp_data(name)
                if as_fp:
                    all_data["as_fp"].append({
                        "type": "as_fp",
                        "name": name,
                        "data": as_fp
                    })
        except Exception as e:
            print(f"Ошибка загрузки АС/ФП: {e}")
        
        # Загружаем настройки
        try:
            settings_files = self.data_manager.list_files("settings")
            for name in settings_files:
                settings = self.data_manager.load_settings(name)
                if settings:
                    all_data["settings"].append({
                        "type": "settings",
                        "name": name,
                        "data": settings
                    })
        except Exception as e:
            print(f"Ошибка загрузки настроек: {e}")
        
        return all_data
    
    def _format_context(self, data: Dict[str, List[Dict[str, Any]]]) -> str:
        """Форматирует данные в текстовый контекст для LLM"""
        context_parts = []
        
        if data.get("news"):
            context_parts.append("=== НОВОСТИ ===")
            for news in data["news"][:10]:  # Ограничиваем количество
                context_parts.append(f"Заголовок: {news.get('title', '')}")
                content = news.get('content', '')
                # Обрезаем длинный контент
                if len(content) > 500:
                    content = content[:500] + "..."
                context_parts.append(f"Содержание: {content}")
                context_parts.append(f"Метка: {news.get('label', '')}")
                context_parts.append("")
        
        if data.get("problems"):
            context_parts.append("=== ПРОБЛЕМЫ ===")
            for problem in data["problems"][:10]:
                problem_data = problem.get("data", {})
                problem_str = json.dumps(problem_data, ensure_ascii=False, indent=2)
                if len(problem_str) > 500:
                    problem_str = problem_str[:500] + "..."
                context_parts.append(f"Проблема: {problem_str}")
                context_parts.append("")
        
        if data.get("deployments"):
            context_parts.append("=== ВНЕДРЕНИЯ ===")
            for deployment in data["deployments"][:10]:
                deployment_data = deployment.get("data", {})
                deployment_str = json.dumps(deployment_data, ensure_ascii=False, indent=2)
                if len(deployment_str) > 500:
                    deployment_str = deployment_str[:500] + "..."
                context_parts.append(f"Название: {deployment.get('name', '')}")
                context_parts.append(f"Данные: {deployment_str}")
                context_parts.append("")
        
        if data.get("infrastructure"):
            context_parts.append("=== ИНФРАСТРУКТУРА ===")
            for infra in data["infrastructure"][:10]:
                infra_data = infra.get("data", {})
                infra_str = json.dumps(infra_data, ensure_ascii=False, indent=2)
                if len(infra_str) > 500:
                    infra_str = infra_str[:500] + "..."
                context_parts.append(f"Название: {infra.get('name', '')}")
                context_parts.append(f"Данные: {infra_str}")
                context_parts.append("")
        
        if data.get("as_fp"):
            context_parts.append("=== АС/ФП ===")
            for as_fp in data["as_fp"][:10]:
                as_fp_data = as_fp.get("data", {})
                as_fp_str = json.dumps(as_fp_data, ensure_ascii=False, indent=2)
                if len(as_fp_str) > 500:
                    as_fp_str = as_fp_str[:500] + "..."
                context_parts.append(f"Название: {as_fp.get('name', '')}")
                context_parts.append(f"Данные: {as_fp_str}")
                context_parts.append("")
        
        if not context_parts:
            return "В системе пока нет данных для ответа на вопросы."
        
        return "\n".join(context_parts)
    
    def _search_relevant_data(self, query: str, all_data: Dict[str, List[Dict[str, Any]]], limit: int = 5) -> Dict[str, List[Dict[str, Any]]]:
        """Простой поиск релевантных данных по ключевым словам"""
        query_lower = query.lower()
        relevant_data = {
            "news": [],
            "problems": [],
            "deployments": [],
            "infrastructure": [],
            "as_fp": [],
            "settings": []
        }
        
        # Поиск в новостях
        for news in all_data.get("news", []):
            title = news.get("title", "").lower()
            content = news.get("content", "").lower()
            if any(word in title or word in content for word in query_lower.split()):
                relevant_data["news"].append(news)
                if len(relevant_data["news"]) >= limit:
                    break
        
        # Поиск в проблемах
        for problem in all_data.get("problems", []):
            problem_str = json.dumps(problem.get("data", {}), ensure_ascii=False).lower()
            if any(word in problem_str for word in query_lower.split()):
                relevant_data["problems"].append(problem)
                if len(relevant_data["problems"]) >= limit:
                    break
        
        # Поиск во внедрениях
        for deployment in all_data.get("deployments", []):
            deployment_str = json.dumps(deployment.get("data", {}), ensure_ascii=False).lower()
            name = deployment.get("name", "").lower()
            if any(word in name or word in deployment_str for word in query_lower.split()):
                relevant_data["deployments"].append(deployment)
                if len(relevant_data["deployments"]) >= limit:
                    break
        
        # Поиск в инфраструктуре
        for infra in all_data.get("infrastructure", []):
            infra_str = json.dumps(infra.get("data", {}), ensure_ascii=False).lower()
            name = infra.get("name", "").lower()
            if any(word in name or word in infra_str for word in query_lower.split()):
                relevant_data["infrastructure"].append(infra)
                if len(relevant_data["infrastructure"]) >= limit:
                    break
        
        # Поиск в АС/ФП
        for as_fp in all_data.get("as_fp", []):
            as_fp_str = json.dumps(as_fp.get("data", {}), ensure_ascii=False).lower()
            name = as_fp.get("name", "").lower()
            if any(word in name or word in as_fp_str for word in query_lower.split()):
                relevant_data["as_fp"].append(as_fp)
                if len(relevant_data["as_fp"]) >= limit:
                    break
        
        return relevant_data
    
    async def generate_response(self, user_message: str, chat_history: List[Dict[str, str]] = None) -> str:
        """Генерирует ответ на вопрос пользователя с использованием контекста данных"""
        try:
            # Проверяем модель при первом использовании
            self._ensure_model_loaded()
            
            # Загружаем все данные
            all_data = self._load_all_data()
            
            # Ищем релевантные данные
            relevant_data = self._search_relevant_data(user_message, all_data)
            
            # Форматируем контекст
            context = self._format_context(relevant_data)
            
            # Формируем промпт
            system_prompt = """Ты - помощник DevOps специалиста. Ты помогаешь отвечать на вопросы по данным системы DevOps Portal.
Используй предоставленный контекст для ответа на вопросы. Если в контексте нет информации для ответа, скажи об этом честно.
Отвечай на русском языке, кратко и по делу."""
            
            user_prompt = f"""Контекст из системы DevOps Portal:

{context}

Вопрос пользователя: {user_message}

Ответь на вопрос пользователя, используя информацию из контекста. Если в контексте нет нужной информации, скажи об этом."""
            
            # Формируем историю сообщений
            messages = [
                {"role": "system", "content": system_prompt}
            ]
            
            # Добавляем историю чата
            if chat_history:
                for msg in chat_history[-5:]:  # Берем последние 5 сообщений
                    messages.append({
                        "role": msg.get("role", "user"),
                        "content": msg.get("content", "")
                    })
            
            # Добавляем текущий вопрос
            messages.append({"role": "user", "content": user_prompt})
            
            # Отправляем запрос в Ollama
            async with httpx.AsyncClient(timeout=60.0) as client:
                try:
                    response = await client.post(
                        f"{self.ollama_host}/api/chat",
                        json={
                            "model": self.model_name,
                            "messages": messages,
                            "stream": False
                        }
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        content = result.get("message", {}).get("content", "")
                        if content:
                            return content
                        else:
                            return "Извините, не удалось получить ответ от LLM. Убедитесь, что Ollama запущен и модель загружена."
                    else:
                        error_text = response.text[:200] if response.text else f"HTTP {response.status_code}"
                        return f"Ошибка подключения к LLM (код {response.status_code}): {error_text}. Убедитесь, что Ollama запущен."
                except httpx.ConnectError:
                    return "Не удалось подключиться к Ollama. Убедитесь, что сервис Ollama запущен и доступен по адресу " + self.ollama_host
                except httpx.TimeoutException:
                    return "Время ожидания ответа от LLM истекло. Попробуйте переформулировать вопрос или подождите немного."
        
        except httpx.TimeoutException:
            return "Извините, время ожидания ответа истекло. Попробуйте переформулировать вопрос."
        except Exception as e:
            print(f"Ошибка генерации ответа: {e}")
            return f"Произошла ошибка при генерации ответа: {str(e)}"

