import zipfile
import io
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict
from config import temp_dir


def unpack(odp_bytes: bytes, filename: str) -> Path:
    stem = Path(filename).stem
    target_dir = temp_dir / stem
    if target_dir.exists():
        shutil.rmtree(target_dir)
    target_dir.mkdir()
    with zipfile.ZipFile(io.BytesIO(odp_bytes), 'r') as zip_ref:
        zip_ref.extractall(target_dir)
    return target_dir


def pack_odp(unpack_dir: Path, output_odp_path: Path):
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


def svg(xml_path: Path, data: Dict[str, str]) -> None:
    with open(xml_path, "r", encoding="utf-8") as f:
        temp = f.read()
    res = temp.format(**data)
    with open(xml_path, "w", encoding="utf-8") as f:
        f.write(res)


def pack_pptx(unpack_dir: Path, output_pptx_path: Path):
    with zipfile.ZipFile(output_pptx_path, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
        for file_path in unpack_dir.rglob('*'):
            if file_path.is_file():
                arcname = file_path.relative_to(unpack_dir)
                zip_ref.write(file_path, arcname)


def replace_placeholders(xml_path: Path, data: Dict[str, str]) -> None:
    # Парсим XML
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # Рекурсивно обходим все элементы
    for elem in root.iter():
        # Заменяем в тексте элемента
        if elem.text:
            for key, val in data.items():
                elem.text = elem.text.replace(f"{{{{{key}}}}}", str(val))
        # Заменяем в хвосте (текст после закрывающего тега)
        if elem.tail:
            for key, val in data.items():
                elem.tail = elem.tail.replace(f"{{{{{key}}}}}", str(val))

    # Записываем изменения обратно
    tree.write(xml_path, encoding='utf-8', xml_declaration=True)
