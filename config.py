from pathlib import Path

# Путь к корневой директории проекта (директория, где находится текущий файл)
BASE_DIR = Path(__file__).parent

# Директория для хранения временных файлов, создаваемых в процессе обработки документов
temp_dir = BASE_DIR / "temp"

# Директория для хранения готовых сгенерированных файлов (PDF и других форматов)
rendered_files_dir = BASE_DIR / "rendered_files"

# Путь к исполняемому файлу LibreOffice для конвертации документов в PDF
# Указан стандартный путь для Windows-установки LibreOffice
soffice_path = r"C:\Program Files\LibreOffice\program\soffice.exe"

# Директория для хранения JSON-файлов с данными, разбитыми по факультетам
faculties_dir = BASE_DIR / "faculties"

# Директория с шаблонами документов (ODP-файлы для каждого факультета)
templates_dir = BASE_DIR / "static" / "templates"