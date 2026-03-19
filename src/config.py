from pathlib import Path

class Settings:
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    BASE_DIR: Path = Path(__file__).resolve().parent
    TEMPLATES_DIR: Path = BASE_DIR / "templates"
    STATIC_DIR: Path = BASE_DIR / "static"
    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    ALLOWED_EXTENSIONS: set = {".svg", ".pptx", ".odp"}
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10 MB

settings = Settings()

settings.UPLOAD_DIR.mkdir(exist_ok=True)
settings.TEMPLATES_DIR.mkdir(exist_ok=True)
settings.STATIC_DIR.mkdir(exist_ok=True)