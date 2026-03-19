from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class FileUploadResponse(BaseModel):
    """Ответ после загрузки файла"""
    success: bool
    filename: str
    message: str
    file_path: Optional[str] = None

class FileInfo(BaseModel):
    """Информация о файле"""
    name: str
    size: int
    extension: str
    uploaded_at: datetime

class UploadHistory(BaseModel):
    """История загрузок"""
    files: List[FileInfo] = []
    total_count: int = 0