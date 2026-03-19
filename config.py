from pathlib import Path

class Settings:
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    BASE_DIR: Path = Path(__file__).parent
    TEMPLATES_DIR: Path = BASE_DIR / "templates"
    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    ALLOWED_EXTENSIONS: set = {".svg", ".pptx", ".odp"}

settings = Settings()
settings.UPLOAD_DIR.mkdir(exist_ok=True)