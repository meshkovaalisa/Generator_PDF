from pathlib import Path

BASE_DIR = Path(__file__).parent
temp_dir = BASE_DIR / "temp"
rendered_files_dir = BASE_DIR / "rendered_files"
soffice_path = r"C:\Program Files\LibreOffice\program\soffice.exe"
depart_info = BASE_DIR / "department_info" / "ИИСиЦТ"


def get_temp_dir() -> Path:
    """Возвращает путь к временной директории."""
    return temp_dir


def get_rendered_files_dir() -> Path:
    """Возвращает путь к директории готовых файлов."""
    return rendered_files_dir
