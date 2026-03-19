from pathlib import Path
from fastapi import UploadFile, HTTPException
from config import settings

class FileService:
    @staticmethod
    async def save_file(file: UploadFile) -> Path:
        ext = Path(file.filename).suffix.lower()
        if ext not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400, 
                detail=f"Разрешены: {', '.join(settings.ALLOWED_EXTENSIONS)}"
            )
        
        file_path = settings.UPLOAD_DIR / file.filename
        content = await file.read()
        
        with open(file_path, "wb") as f:
            f.write(content)
        
        return file_path
    
    @staticmethod
    def get_all_files() -> list:
        if not settings.UPLOAD_DIR.exists():
            return []
        return [f.name for f in settings.UPLOAD_DIR.iterdir() if f.is_file()]

file_service = FileService()