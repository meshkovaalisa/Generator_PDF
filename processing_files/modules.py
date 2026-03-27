import zipfile
import io
import shutil
from pathlib import Path
from typing import Dict
from config import temp_dir
from lxml import etree


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


def pack_pptx(unpack_dir: Path, output_pptx_path: Path):
    with zipfile.ZipFile(output_pptx_path, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
        for file_path in unpack_dir.rglob('*'):
            if file_path.is_file():
                arcname = file_path.relative_to(unpack_dir)
                zip_ref.write(file_path, arcname)


def replace_placeholders(xml_path: Path, data: dict[str, str]) -> None:
    # Парсим с сохранением исходных префиксов
    parser = etree.XMLParser(remove_blank_text=False)
    tree = etree.parse(str(xml_path), parser)
    root = tree.getroot()

    # Рекурсивно обходим все элементы
    for elem in root.iter():
        if elem.text:
            for key, val in data.items():
                elem.text = elem.text.replace(f"{{{{{key}}}}}", str(val))
        if elem.tail:
            for key, val in data.items():
                elem.tail = elem.tail.replace(f"{{{{{key}}}}}", str(val))

    # Записываем обратно, сохраняя исходные префиксы
    tree.write(str(xml_path), encoding='utf-8', xml_declaration=True, pretty_print=False)