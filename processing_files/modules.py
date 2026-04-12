import zipfile, uuid , io, shutil, re
from pathlib import Path
from typing import Dict
from config import temp_dir
from pydantic import BaseModel

class FacultyRequest(BaseModel):
    faculty_name: str

def replace_placeholders_in_slide(slide_element, data: Dict[str, str]) -> None:
    """
    Замена плейсхолдеров в одном слайде.
    """
    placeholders = {f"{{{{{key}}}}}": str(val) for key, val in data.items()}

    # Ищем все текстовые элементы внутри слайда
    for elem in slide_element.iter():
        if elem.text:
            for placeholder, value in placeholders.items():
                if placeholder in elem.text:
                    elem.text = elem.text.replace(placeholder, value)
        if elem.tail:
            for placeholder, value in placeholders.items():
                if placeholder in elem.tail:
                    elem.tail = elem.tail.replace(placeholder, value)


def remove_unmatched_placeholders(slide, used_keys):
    # Получаем все элементы с текстом
    for element in slide.iter():
        if element.text:

            placeholders = re.findall(r'\{\{([^}]+)\}\}', element.text)

            for placeholder in placeholders:
                if placeholder not in used_keys:
                    # Удаляем незадействованный плейсхолдер
                    element.text = element.text.replace(f"{{{{{placeholder}}}}}", "")

def random_file_name():

    unique_name = uuid.uuid4().hex

    return unique_name



def unpack(odp_bytes: bytes, filename: str) -> Path:
    """
    Распаковка и сохранение файла в виде xml во временную дирректорию

    Args:
        odp_bytes (bytes): Содержимое файла-шаблона в виде байтов
        filename (str): Имя исходного файла (используется для названия папки)

    Returns:
        Path: Путь к созданной директории с распакованным содержимым
    """
    stem = Path(filename).stem
    target_dir = temp_dir / stem
    if target_dir.exists():
        shutil.rmtree(target_dir)
    target_dir.mkdir()
    with zipfile.ZipFile(io.BytesIO(odp_bytes), 'r') as zip_ref:
        zip_ref.extractall(target_dir)
    return target_dir


def pack_odp(unpack_dir: Path, output_odp_path: Path) -> None:
    """
    Запаковка распакованной директории обратно в файл формата .odp.

    Args:
        unpack_dir (Path): Путь к директории с распакованным содержимым .odp
        output_odp_path (Path): Путь для сохранения результирующего .odp файла

    Raises:
        FileNotFoundError: Если в директории отсутствует файл 'mimetype'
    """
    mimetype_file = unpack_dir / 'mimetype'
    if not mimetype_file.exists():
        raise FileNotFoundError("mimetype not found")
    all_files = [f for f in unpack_dir.rglob('*') if f.is_file() and f != mimetype_file]
    with zipfile.ZipFile(output_odp_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Сначала mimetype без сжатия
        zipf.write(mimetype_file, 'mimetype', compress_type=zipfile.ZIP_STORED)
        for f in all_files:
            arcname = f.relative_to(unpack_dir)
            zipf.write(f, arcname)


def pack_pptx(unpack_dir: Path, output_pptx_path: Path) -> None:
    """
    Запаковка распакованной директории обратно в файл формата .pptx.

    Args:
        unpack_dir (Path): Путь к директории с распакованным содержимым .pptx
        output_pptx_path (Path): Путь для сохранения результирующего .pptx файла
    """
    with zipfile.ZipFile(output_pptx_path, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
        for file_path in unpack_dir.rglob('*'):
            if file_path.is_file():
                arcname = file_path.relative_to(unpack_dir)
                zip_ref.write(file_path, arcname)


