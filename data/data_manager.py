import json
import yaml
import os
from pathlib import Path
from typing import Dict, Any, List, Optional

class DataManager:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Создаем поддиректории для разных типов данных
        (self.data_dir / "as_fp").mkdir(exist_ok=True)
        (self.data_dir / "settings").mkdir(exist_ok=True)
        (self.data_dir / "deployments").mkdir(exist_ok=True)
        (self.data_dir / "infrastructure").mkdir(exist_ok=True)
        (self.data_dir / "ai_chat").mkdir(exist_ok=True)
    
    def save_json(self, filename: str, data: Dict[str, Any], subdir: str = "") -> bool:
        """Сохранение данных в JSON файл"""
        try:
            file_path = self.data_dir / subdir / f"{filename}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Ошибка сохранения JSON: {e}")
            return False
    
    def load_json(self, filename: str, subdir: str = "") -> Optional[Dict[str, Any]]:
        """Загрузка данных из JSON файла"""
        try:
            file_path = self.data_dir / subdir / f"{filename}.json"
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return None
        except Exception as e:
            print(f"Ошибка загрузки JSON: {e}")
            return None
    
    def save_yaml(self, filename: str, data: Dict[str, Any], subdir: str = "") -> bool:
        """Сохранение данных в YAML файл"""
        try:
            file_path = self.data_dir / subdir / f"{filename}.yaml"
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
            return True
        except Exception as e:
            print(f"Ошибка сохранения YAML: {e}")
            return False
    
    def load_yaml(self, filename: str, subdir: str = "") -> Optional[Dict[str, Any]]:
        """Загрузка данных из YAML файла"""
        try:
            file_path = self.data_dir / subdir / f"{filename}.yaml"
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)
            return None
        except Exception as e:
            print(f"Ошибка загрузки YAML: {e}")
            return None
    
    def list_files(self, subdir: str = "", extension: str = "json") -> List[str]:
        """Получение списка файлов в директории"""
        try:
            dir_path = self.data_dir / subdir
            if dir_path.exists():
                return [f.stem for f in dir_path.glob(f"*.{extension}")]
            return []
        except Exception as e:
            print(f"Ошибка получения списка файлов: {e}")
            return []
    
    def delete_file(self, filename: str, subdir: str = "", extension: str = "json") -> bool:
        """Удаление файла"""
        try:
            file_path = self.data_dir / subdir / f"{filename}.{extension}"
            if file_path.exists():
                file_path.unlink()
                return True
            return False
        except Exception as e:
            print(f"Ошибка удаления файла: {e}")
            return False
    
    # Специфичные методы для разных типов данных
    def save_as_fp_data(self, name: str, data: Dict[str, Any]) -> bool:
        """Сохранение данных АС/ФП"""
        return self.save_json(name, data, "as_fp")
    
    def load_as_fp_data(self, name: str) -> Optional[Dict[str, Any]]:
        """Загрузка данных АС/ФП"""
        return self.load_json(name, "as_fp")
    
    def save_settings(self, name: str, data: Dict[str, Any]) -> bool:
        """Сохранение настроек"""
        return self.save_json(name, data, "settings")
    
    def load_settings(self, name: str) -> Optional[Dict[str, Any]]:
        """Загрузка настроек"""
        return self.load_json(name, "settings")
    
    def save_deployment(self, name: str, data: Dict[str, Any]) -> bool:
        """Сохранение данных о внедрениях"""
        return self.save_json(name, data, "deployments")
    
    def load_deployment(self, name: str) -> Optional[Dict[str, Any]]:
        """Загрузка данных о внедрениях"""
        return self.load_json(name, "deployments")
    
    def save_infrastructure(self, name: str, data: Dict[str, Any]) -> bool:
        """Сохранение инфраструктурных данных"""
        return self.save_json(name, data, "infrastructure")
    
    def load_infrastructure(self, name: str) -> Optional[Dict[str, Any]]:
        """Загрузка инфраструктурных данных"""
        return self.load_json(name, "infrastructure") 