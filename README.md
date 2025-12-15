## DevOps Service Portal

Веб‑портал для управления DevOps‑процессами и инфраструктурой, построенный на FastAPI.  
Боевой пример развёрнут на `https://devops.pirantelx.ru/`.

---

## 1. Пользовательское описание и сценарии использования

### 1.1. Назначение системы

DevOps Service Portal решает задачу **централизованного управления DevOps‑активностями**:

- хранение и просмотр сведений об АС/ФП;
- ведение новостей и служебной информации;
- управление внедрениями и инфраструктурными работами;
- учёт проблем и рисков;
- **чат с ИИ**, который отвечает на вопросы по данным портала (новости, проблемы, внедрения, инфраструктура и др.);
- валидатор шаблонов (Jinja2 / Helm / YAML) в разделе **«Шаблонизация»**.

### 1.2. Основные пользовательские сценарии

- **Регистрация и вход**
  - Пользователь открывает `https://devops.pirantelx.ru/` или `http://localhost:8000/`.
  - При отсутствии учётки — переходит на `/register`, заполняет форму (логин, роль, пароль).
  - Затем входит на `/login`. После входа попадает в чат с ИИ (главная страница).

- **Чат с ИИ (главная страница)**
  - Ввод вопроса в поле «Введите ваш вопрос…».
  - ИИ использует данные из:
    - новостей (`data/news/news.json`),
    - проблем и рисков (`data/problems/problems.json`),
    - внедрений (`data/deployments/*.json`),
    - инфраструктуры (`data/infrastructure/*.json`),
    - АС/ФП (`data/as_fp/*.json`),
  - и формирует ответ, показывая его в переписке.
  - История чата сохраняется в `data/ai_chat/<username>.json`.

- **Сведения об АС/ФП (`/as-fp`)**
  - Просмотр списка АС/ФП.
  - Переход к деталям конкретной системы.
  - Данные берутся из JSON‑файлов в `data/as_fp/`.

- **Шаблонизация (`/settings`)**
  - Вставка кода шаблона (Jinja2 / Helm / YAML) в левый блок.
  - В правом блоке — ввод JSON с переменными (placeholders).
  - Нажатие «Рендерить и проверить»:
    - шаблон рендерится на сервере (для Jinja2);
    - результат проверяется валидатором (`TemplateValidator`):
      - синтаксис Jinja2,
      - YAML‑валидность,
      - корректность Helm‑директив;
    - пользователь видит ошибки/предупреждения и (опционально) отрендеренный результат.

- **Автономные внедрения (`/deployments`)**
  - Просмотр списка внедрений (JSON‑файлы в `data/deployments/`).
  - Переход к деталям внедрения.

- **Новости (`/news`)**
  - Создание/редактирование/удаление новостей.
  - Фильтрация, поиск, пагинация.

- **Проблемы и риски (`/problems`)**
  - Просмотр списка проблем/рисков (JSON в `data/problems/problems.json`).

- **Инфраструктурные работы (`/infrastructure`)**
  - Просмотр списка работ, планирование и описание.

- **Профиль (`/profile`)**
  - Просмотр имени пользователя, роли, ФИО сотрудника.
  - Переход к редактированию профиля (при необходимости).

### 1.3. Сценарии тестирования (минимальный чек‑лист)

- Регистрация нового пользователя и вход.
- Проверка доступа к разделам без авторизации (должен редиректить/показывать логин).
- Отправка вопросов в чат с ИИ и получение ответа.
- Создание новости, её отображение в списке, редактирование и удаление.
- Открытие «Шаблонизации», вставка:
  - корректного YAML,
  - YAML с ошибкой,
  - Jinja2 шаблона с корректным синтаксисом,
  - Jinja2 шаблона с ошибкой.
- Проверка, что ошибки отображаются пользователю внятно.

---

## 2. Описание кода программы

### 2.1. Общая архитектура

- **FastAPI приложение** — точка входа `main.py`.
- **Маршруты** — каталог `routes/`, каждый модуль отвечает за свою область.
- **Авторизация и пользователи** — каталог `auth/`.
- **Работа с данными (JSON/YAML)** — `data/data_manager.py`, `data/news_manager.py`.
- **Сервисы** — `services/`:
  - `llm_service.py` — интеграция с LLM (Ollama, RAG по данным системы);
  - `template_validator.py` — валидация Jinja2/Helm/YAML.
- **Шаблоны** — `templates/` (Jinja2, Bootstrap 5).

### 2.2. Основные модули

#### `main.py`

- Создаёт объект FastAPI.
- Подключает роуты (`routes.main`, `routes.auth`, `routes.as_fp`, `routes.settings`, `routes.deployments`, `routes.infrastructure`, `routes.ai_chat`, `routes.news`, `routes.problems`).
- Запускает uvicorn при запуске как `__main__`.

#### `auth/`

- `auth.py` — логика аутентификации:
  - проверка пароля,
  - получение текущего пользователя из JWT токена или cookie;
- `models.py` — Pydantic‑модели: `User`, `UserCreate`, `UserLogin`, `Token`, `News` и др.;
- `utils.py` — хеширование паролей, работа с JWT, загрузка/сохранение пользователей в `data/users/users.json`.

#### `routes/auth.py`

- `/login`, `/register`, `/logout`, `/profile`, `/profile/edit`.
- Использует `auth.auth` и `auth.utils`.
- При логине выставляет cookie `access_token` с JWT.

#### `routes/ai_chat.py`

- `/ai-chat` — страница чата.
- `/ai-chat/message` — API для отправки сообщения.
- Использует `services.llm_service.LLMService`:
  - собирает историю чата;
  - передаёт её и вопрос пользователя в LLM;
  - сохраняет ответ ИИ.

#### `services/llm_service.py`

- Работает с Ollama (локальный LLM‑движок):
  - подтягивает модель (по умолчанию `llama3.2:1b`, настраивается через `OLLAMA_MODEL`);
  - собирает данные из `data/` (новости, проблемы, внедрения, инфраструктура, АС/ФП);
  - формирует текстовый контекст;
  - отправляет запрос в `/api/chat` Ollama и получает ответ;
  - обрабатывает ошибки/таймауты и возвращает понятное сообщение пользователю.

#### `services/template_validator.py`

- `TemplateValidator`:
  - `validate_jinja` — проверка синтаксиса Jinja2, поиск необъявленных переменных;
  - `validate_helm` — проверка YAML + поиска Helm‑директив и типичных ошибок;
  - `validate_file` — автоопределение типа файла по имени и содержимому и запуск нужных проверок.

#### `routes/settings.py` (раздел «Шаблонизация»)

- `/settings` — страница вставки шаблона и переменных.
- `/settings/validate` — API для валидации текста шаблона.
- `/settings/validate-upload` — API для валидации загруженного файла.
- `/settings/render` — API для рендеринга Jinja2 шаблона с переменными (используется UI).

#### `data/data_manager.py`

- Универсальные методы:
  - `save_json`, `load_json`, `save_yaml`, `load_yaml`, `list_files`, `delete_file`;
- Специализированные методы:
  - `save_as_fp_data`, `load_as_fp_data`;
  - `save_settings`, `load_settings`;
  - `save_deployment`, `load_deployment`;
  - `save_infrastructure`, `load_infrastructure`;
  - `save_news_data`, `load_news_data`;
  - `save_problems_data`, `load_problems_data`;
  - методы работы с историей чата.

### 2.3. Комментарии в коде

Код снабжён комментариями в ключевых местах:

- внутри роутов (описания эндпоинтов);
- в сервисах (`llm_service.py`, `template_validator.py`) — объяснение логики RAG и валидации;
- в менеджерах данных (`data_manager.py`, `news_manager.py`).

Для детального изучения кода достаточно открыть соответствующие файлы в IDE — структура модуля и комментарии проведут по логике.

---

## 3. Установка и запуск

Ниже — **две** схемы установки: локальная (для разработки) и Docker/Compose (как на `devops.pirantelx.ru`).

### 3.1. Локальная установка (Windows / Linux / macOS)

#### Шаг 1. Клонирование репозитория

```bash
git clone <repository-url>
cd devops-service/devops-service
```

#### Шаг 2. Создание и активация виртуального окружения

```bash
python -m venv venv
```

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/macOS:**
```bash
source venv/bin/activate
```

#### Шаг 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

#### Шаг 4. Запуск приложения

```bash
python main.py
```

или:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Шаг 5. Доступ к приложению

Откройте браузер и перейдите по адресу `http://localhost:8000/`.

### 3.2. Установка через Docker Compose (как на `https://devops.pirantelx.ru/`)

1. Установить Docker и Docker Compose.
2. В корне проекта (где лежит `docker-compose.yml`):

   ```bash
   docker-compose up -d
   ```

   В составе:
   - **app-devops** — контейнер с FastAPI приложением (каталог `devops-service/` монтируется в `/opt/app`);
   - **nginx** — фронтенд‑прокси (`proxy/nginx.conf`), проксирует 80/443 на FastAPI;
   - опционально — контейнер с **Ollama** (если включён в `docker-compose.yml`) для работы LLM.

3. Для HTTPS используется **certbot** и конфигурация в `certbot/` (как на `devops.pirantelx.ru`):
   - сертификаты в `certbot/conf/live/devops.pirantelx.ru/`;
   - nginx использует их для TLS‑терминации.

4. После старта:
   - открыть `http://localhost/` или домен (например, `https://devops.pirantelx.ru/`);
   - зарегистрировать пользователя и войти.

5. Для обновления кода:
   ```bash
   git pull
   docker-compose restart app-devops
   ```

### 3.3. Проверка установки на чистой машине (пример)

1. Установить `git`, `python3`, `pip`.
2. Выполнить шаги из **3.1** (клонирование, venv, `pip install -r requirements.txt`, `python main.py`).
3. Открыть браузер и пройти сценарий:
   - регистрация → вход → открытие чата → отправка вопроса;
   - переход в «Шаблонизацию» и проверка простого YAML.
4. Убедиться, что ошибок в консоли нет, страницы отрабатывают корректно.

---

## 4. Код программы (обзор с примерами)

Ниже — краткий обзор ключевых файлов с примерами. Полный код с комментариями находится в репозитории.

### 4.1. Пример: LLM‑сервис (`services/llm_service.py`)

```python
class LLMService:
    def __init__(self, ollama_host: str = None):
        self.ollama_host = ollama_host or os.getenv("OLLAMA_HOST", "http://localhost:11434")
        # Лёгкая модель по умолчанию, можно переопределить переменной окружения
        self.model_name = os.getenv("OLLAMA_MODEL", "llama3.2:1b")
        self.data_manager = DataManager()
        self.news_manager = NewsManager()
        self._model_checked = False

    def _ensure_model_loaded(self):
        """Проверяет и при необходимости подтягивает модель в Ollama."""
        if self._model_checked:
            return
        ...

    async def generate_response(self, user_message: str, chat_history: List[Dict[str, str]] = None) -> str:
        """Генерация ответа с использованием данных портала и LLM."""
        self._ensure_model_loaded()
        all_data = self._load_all_data()
        relevant_data = self._search_relevant_data(user_message, all_data)
        context = self._format_context(relevant_data)
        ...
```

### 4.2. Пример: валидация шаблонов (`services/template_validator.py`)

```python
class TemplateValidator:
    """Валидатор для Jinja2 и Helm шаблонов."""

    def __init__(self):
        self.jinja_env = Environment()

    def validate_jinja(self, template_content: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Проверка синтаксиса Jinja2, поиск переменных и ошибок рендеринга."""
        ...

    def validate_helm(self, template_content: str, chart_type: str = "template") -> Dict[str, Any]:
        """Проверка Helm/YAML, подсветка типичных ошибок."""
        ...
```

### 4.3. Пример: раздел «Шаблонизация» (`routes/settings.py`)

```python
@router.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    """Страница шаблонизации и проверки конфигураций."""
    current_user = await get_current_user_from_request(request)
    if not current_user:
        return templates.TemplateResponse("login.html", {"request": request})
    return templates.TemplateResponse("settings.html", {"request": request, "user": current_user})
```

Шаблон `templates/check-settings/settings.html` содержит UI для вставки шаблона, ввода JSON‑переменных и отображения результатов проверки.

---

## 5. Технологии

- **Backend**: FastAPI (Python 3.13 в Docker образе)
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Шаблоны**: Jinja2
- **Хранение данных**: JSON файлы в каталоге `data/`
- **Аутентификация**: JWT + cookie `access_token`
- **LLM**: Ollama (локальный LLM‑движок, опционален)

---

## 6. Лицензия и поддержка

- Лицензия: **MIT License**
- Для вопросов и предложений — создайте issue в репозитории или свяжитесь с автором проекта.