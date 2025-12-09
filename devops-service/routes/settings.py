from fastapi import APIRouter, Request, HTTPException, status, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional, Dict, Any
from jinja2 import Environment, Template
from auth.auth import get_current_user_from_request
from data.data_manager import DataManager
from services.template_validator import TemplateValidator

router = APIRouter()
templates = Jinja2Templates(
    directory=["./templates/check-settings", "./templates/main"]
)
data_manager = DataManager()
# Инициализируем валидатор лениво, чтобы не блокировать запуск
validator = None

def get_validator():
    """Ленивая инициализация TemplateValidator"""
    global validator
    if validator is None:
        validator = TemplateValidator()
    return validator

class ValidateRequest(BaseModel):
    content: str
    filename: Optional[str] = None
    template_type: Optional[str] = None  # "jinja" or "helm"

class RenderRequest(BaseModel):
    template: str
    variables: Dict[str, Any] = {}

@router.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    """Страница проверки настроек"""
    try:
        current_user = await get_current_user_from_request(request)
        if not current_user:
            return templates.TemplateResponse("login.html", {"request": request})
        
        # settings_list больше не используется в новом шаблоне, но оставляем для совместимости
        settings_list = data_manager.list_files("settings")
        settings_data = []
        for name in settings_list:
            try:
                data = data_manager.load_settings(name)
                if data:
                    settings_data.append({"name": name, "data": data})
            except Exception as e:
                print(f"Ошибка загрузки настроек {name}: {e}")
                continue
        
        return templates.TemplateResponse("settings.html", {
            "request": request, 
            "user": current_user, 
            "settings_list": settings_data
        })
    except Exception as e:
        print(f"Ошибка в settings_page: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка загрузки страницы: {str(e)}"
        )

@router.get("/settings/{name}", response_class=HTMLResponse)
async def settings_detail(request: Request, name: str):
    current_user = await get_current_user_from_request(request)
    if not current_user:
        return templates.TemplateResponse("login.html", {"request": request})
    
    data = data_manager.load_settings(name)
    return templates.TemplateResponse("settings_detail.html", {"request": request, "user": current_user, "settings": data, "name": name})

@router.get("/settings/create", response_class=HTMLResponse)
async def settings_create_page(request: Request):
    """Страница создания новых настроек"""
    current_user = await get_current_user_from_request(request)
    if not current_user:
        return templates.TemplateResponse("login.html", {"request": request})
    
    return templates.TemplateResponse("settings_create.html", {
        "request": request,
        "user": current_user
    })

@router.post("/settings/validate")
async def validate_template(request: Request, validate_req: ValidateRequest):
    """API endpoint для валидации шаблона"""
    current_user = await get_current_user_from_request(request)
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Необходима авторизация"
        )
    
    try:
        content = validate_req.content
        filename = validate_req.filename or "template"
        template_type = validate_req.template_type
        
        val = get_validator()
        if template_type == "jinja":
            result = val.validate_jinja(content)
            return JSONResponse({
                "type": "jinja",
                "validation": result
            })
        elif template_type == "helm":
            result = val.validate_helm(content)
            return JSONResponse({
                "type": "helm",
                "validation": result
            })
        else:
            # Автоматическое определение типа
            result = val.validate_file(filename, content)
            return JSONResponse(result)
    
    except Exception as e:
        return JSONResponse(
            {
                "type": "error",
                "validation": {
                    "valid": False,
                    "errors": [{"message": f"Ошибка валидации: {str(e)}"}],
                    "warnings": []
                }
            },
            status_code=500
        )

@router.post("/settings/validate-upload")
async def validate_uploaded_file(
    request: Request,
    file: UploadFile = File(...)
):
    """API endpoint для валидации загруженного файла"""
    current_user = await get_current_user_from_request(request)
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Необходима авторизация"
        )
    
    try:
        # Читаем содержимое файла
        content = await file.read()
        content_str = content.decode('utf-8')
        filename = file.filename or "uploaded_file"
        
        # Валидируем файл
        val = get_validator()
        result = val.validate_file(filename, content_str)
        
        return JSONResponse(result)
    
    except UnicodeDecodeError:
        return JSONResponse(
            {
                "type": "error",
                "validation": {
                    "valid": False,
                    "errors": [{"message": "Файл не является текстовым или содержит недопустимые символы"}],
                    "warnings": []
                }
            },
            status_code=400
        )
    except Exception as e:
        return JSONResponse(
            {
                "type": "error",
                "validation": {
                    "valid": False,
                    "errors": [{"message": f"Ошибка обработки файла: {str(e)}"}],
                    "warnings": []
                }
            },
            status_code=500
        )

@router.post("/settings/render")
async def render_template_endpoint(request: Request, render_req: RenderRequest):
    """API endpoint для рендеринга шаблона с переменными"""
    current_user = await get_current_user_from_request(request)
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Необходима авторизация"
        )
    
    try:
        template_content = render_req.template
        variables = render_req.variables or {}
        
        # Создаем Jinja2 окружение
        jinja_env = Environment()
        
        # Рендерим шаблон
        template = jinja_env.from_string(template_content)
        rendered = template.render(**variables)
        
        return JSONResponse({
            "rendered": rendered,
            "status": "success"
        })
    
    except Exception as e:
        return JSONResponse(
            {
                "rendered": None,
                "status": "error",
                "error": str(e)
            },
            status_code=500
        ) 