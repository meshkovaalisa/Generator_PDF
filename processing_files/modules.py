import zipfile
import io
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict
from config import temp_dir



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


def replace_placeholders(xml_path: Path, data: Dict[str, str]) -> None:
    """
    Замена плейсхолдеров в XML-файле на значения из словаря.

    Args:
        xml_path (Path): Путь к XML-файлу для модификации
        data (Dict[str, str]): Словарь замен, где ключ — имя плейсхолдера,
                               значение — текст для подстановки
    """
    # Парсим XML
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # Рекурсивно обходим все элементы
    for elem in root.iter():
        if elem.text:
            for key, val in data.items():
                elem.text = elem.text.replace(f"{{{{{key}}}}}", str(val))
        if elem.tail:
            for key, val in data.items():
                elem.tail = elem.tail.replace(f"{{{{{key}}}}}", str(val))

    # Записываем изменения обратно
    tree.write(xml_path, encoding='utf-8', xml_declaration=True)


def zip_and_save(folder, output_dir: Path):
    """
    Сохраняет ZIP архив на диск

    Args:
        folder: папка для архивации
        output_dir: директория для сохранения ZIP файла

    Returns:
        Path: путь к созданному ZIP файлу
    """
    # Создаем имя ZIP файла на основе имени папки
    zip_filename = output_dir / f"{folder.name}.zip"

    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for file_path in folder.rglob("*"):
            if file_path.is_file():
                arcname = file_path.relative_to(folder.parent)
                zip_file.write(file_path, arcname=arcname)

    return zip_filename
