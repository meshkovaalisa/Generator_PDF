from pathlib import Path
from typing import Tuple, Optional
from datetime import datetime
from config import settings
from datetime import datetime

def validate_file_extension(filename: str) -> Tuple[bool, str]:
    """Проверка расширения файла"""
    if not filename:
        return False, "Имя файла не указано"
    
    ext = Path(filename).suffix.lower()
    
    if ext not in settings.ALLOWED_EXTENSIONS:
        return False, f"Недопустимый формат. Разрешены: {', '.join(settings.ALLOWED_EXTENSIONS)}"
    
    return True, "OK"

def validate_file_size(file_size: int) -> Tuple[bool, str]:
    """Проверка размера файла"""
    if file_size > settings.MAX_FILE_SIZE:
        return False, f"Файл слишком большой. Максимум: {settings.MAX_FILE_SIZE // 1024 // 1024} MB"
    
    return True, "OK"

def get_file_info(file_path: Path) -> dict:
    """Получение информации о файле"""
    return {
        "name": file_path.name,
        "size": file_path.stat().st_size,
        "extension": file_path.suffix,
        "uploaded_at": datetime.fromtimestamp(file_path.stat().st_mtime)
    }

def generate_unique_filename(filename: str) -> str:
    """Генерация уникального имени файла"""
    import uuid
    name = Path(filename).stem
    ext = Path(filename).suffix
    
    return f"{name}_{uuid.uuid4().hex[:8]}{ext}"