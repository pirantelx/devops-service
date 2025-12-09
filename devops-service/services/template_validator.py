import re
import yaml
from typing import Dict, List, Any, Optional, Tuple
from jinja2 import Environment, TemplateSyntaxError, UndefinedError
from jinja2.meta import find_undeclared_variables


class TemplateValidator:
    """Валидатор для Jinja2 и Helm шаблонов"""
    
    def __init__(self):
        self.jinja_env = Environment()
    
    def validate_jinja(self, template_content: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Валидация Jinja2 шаблона
        
        Args:
            template_content: Содержимое шаблона
            context: Опциональный контекст для проверки переменных
        
        Returns:
            Словарь с результатами валидации
        """
        result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "variables": [],
            "syntax_ok": False
        }
        
        try:
            # Парсим шаблон для проверки синтаксиса
            template = self.jinja_env.parse(template_content)
            result["syntax_ok"] = True
            
            # Находим необъявленные переменные
            try:
                ast = self.jinja_env.parse(template_content)
                undeclared = find_undeclared_variables(ast)
                result["variables"] = list(undeclared)
                
                # Если есть контекст, проверяем, все ли переменные определены
                if context:
                    missing_vars = [var for var in undeclared if var not in context]
                    if missing_vars:
                        result["warnings"].append(
                            f"Переменные не определены в контексте: {', '.join(missing_vars)}"
                        )
                elif undeclared:
                    result["warnings"].append(
                        f"Найдены переменные, которые могут быть не определены: {', '.join(undeclared)}"
                    )
            except Exception as e:
                result["warnings"].append(f"Не удалось проанализировать переменные: {str(e)}")
            
            # Пытаемся отрендерить шаблон с пустым контекстом для проверки
            try:
                test_template = self.jinja_env.from_string(template_content)
                test_template.render(context or {})
            except UndefinedError as e:
                result["warnings"].append(f"Неопределенная переменная при рендеринге: {str(e)}")
            except Exception as e:
                result["warnings"].append(f"Предупреждение при рендеринге: {str(e)}")
        
        except TemplateSyntaxError as e:
            result["valid"] = False
            result["syntax_ok"] = False
            result["errors"].append({
                "message": f"Синтаксическая ошибка: {e.message}",
                "line": e.lineno,
                "filename": e.filename or "template"
            })
        except Exception as e:
            result["valid"] = False
            result["errors"].append({
                "message": f"Ошибка валидации: {str(e)}",
                "line": None,
                "filename": "template"
            })
        
        return result
    
    def validate_helm(self, template_content: str, chart_type: str = "template") -> Dict[str, Any]:
        """
        Валидация Helm шаблона
        
        Args:
            template_content: Содержимое Helm шаблона
            chart_type: Тип файла (template, values, Chart.yaml)
        
        Returns:
            Словарь с результатами валидации
        """
        result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "is_yaml": False,
            "has_helm_directives": False,
            "helm_errors": []
        }
        
        # Проверяем, является ли файл YAML
        try:
            yaml_data = yaml.safe_load(template_content)
            result["is_yaml"] = True
            
            # Для Chart.yaml проверяем обязательные поля
            if chart_type == "Chart.yaml":
                required_fields = ["apiVersion", "name", "version"]
                for field in required_fields:
                    if field not in yaml_data:
                        result["errors"].append(f"Отсутствует обязательное поле: {field}")
                        result["valid"] = False
        except yaml.YAMLError as e:
            result["valid"] = False
            result["errors"].append({
                "message": f"Ошибка YAML: {str(e)}",
                "line": getattr(e, 'problem_mark', None),
                "filename": "template"
            })
            return result
        
        # Проверяем наличие Helm директив ({{ }})
        helm_pattern = r'\{\{.*?\}\}'
        helm_matches = re.findall(helm_pattern, template_content)
        result["has_helm_directives"] = len(helm_matches) > 0
        
        # Проверяем Jinja2 синтаксис внутри Helm директив
        if result["has_helm_directives"]:
            jinja_result = self.validate_jinja(template_content)
            if not jinja_result["valid"]:
                result["valid"] = False
                result["helm_errors"] = jinja_result["errors"]
                result["errors"].extend(jinja_result["errors"])
            if jinja_result["warnings"]:
                result["warnings"].extend(jinja_result["warnings"])
        
        # Проверяем типичные ошибки Helm
        # Проверка на неправильное использование .Values, .Release и т.д.
        invalid_patterns = [
            (r'\.Values\s*\.', "Неправильное использование .Values (должно быть .Values.field)"),
            (r'\.Release\s*\.', "Неправильное использование .Release (должно быть .Release.field)"),
        ]
        
        for pattern, message in invalid_patterns:
            if re.search(pattern, template_content):
                result["warnings"].append(message)
        
        # Проверяем правильность использования функций Helm
        helm_functions = [
            'include', 'required', 'tpl', 'default', 'empty', 'coalesce',
            'toYaml', 'toJson', 'b64enc', 'b64dec', 'indent', 'nindent'
        ]
        
        for func in helm_functions:
            # Проверяем, что функции используются правильно
            func_pattern = r'\{\{\s*' + func + r'\s*[^(]'
            if re.search(func_pattern, template_content):
                result["warnings"].append(
                    f"Возможно неправильное использование функции {func} (проверьте синтаксис)"
                )
        
        return result
    
    def validate_file(self, filename: str, content: str) -> Dict[str, Any]:
        """
        Автоматическое определение типа файла и валидация
        
        Args:
            filename: Имя файла
            content: Содержимое файла
        
        Returns:
            Словарь с результатами валидации
        """
        filename_lower = filename.lower()
        
        # Определяем тип файла
        if filename_lower.endswith('.yaml') or filename_lower.endswith('.yml'):
            if 'chart.yaml' in filename_lower or 'Chart.yaml' in filename:
                return {
                    "type": "helm_chart",
                    "validation": self.validate_helm(content, "Chart.yaml")
                }
            elif 'values.yaml' in filename_lower or 'values.yml' in filename:
                return {
                    "type": "helm_values",
                    "validation": self.validate_helm(content, "values")
                }
            elif any(x in filename_lower for x in ['template', 'templates']):
                return {
                    "type": "helm_template",
                    "validation": self.validate_helm(content, "template")
                }
            else:
                # Обычный YAML
                try:
                    yaml.safe_load(content)
                    return {
                        "type": "yaml",
                        "validation": {
                            "valid": True,
                            "errors": [],
                            "warnings": [],
                            "is_yaml": True
                        }
                    }
                except yaml.YAMLError as e:
                    return {
                        "type": "yaml",
                        "validation": {
                            "valid": False,
                            "errors": [{"message": f"Ошибка YAML: {str(e)}"}],
                            "warnings": [],
                            "is_yaml": False
                        }
                    }
        
        elif filename_lower.endswith('.j2') or filename_lower.endswith('.jinja') or filename_lower.endswith('.jinja2'):
            return {
                "type": "jinja",
                "validation": self.validate_jinja(content)
            }
        
        elif '{{' in content and '}}' in content:
            # Файл содержит Helm/Jinja директивы
            if '.yaml' in filename_lower or '.yml' in filename_lower:
                return {
                    "type": "helm_template",
                    "validation": self.validate_helm(content, "template")
                }
            else:
                return {
                    "type": "jinja",
                    "validation": self.validate_jinja(content)
                }
        
        else:
            return {
                "type": "unknown",
                "validation": {
                    "valid": False,
                    "errors": [{"message": "Не удалось определить тип файла"}],
                    "warnings": [],
                }
            }

