import shutil
from pathlib import Path
from typing import Dict
from symtable import Class

from processing_files.modules import unpack, pack_odp, pack_pptx, replace_placeholders
from config import temp_dir


def handler_file(file:str, data: Dict[str, str]):
    """
    Проверка формата файла и передача в следующие функции для заполнения

    Args:
        file (str): путь для сохраненного файла шаблона
        data (Dict[str, str]): данные из файла .json

    Returns:
        Path: путь для сохранения результирующего файла
    """
    output_file = None
    source = Path(temp_dir / file)

    if not source.exists():
        print("Файл не найден")
        return

    with open(source, "rb") as f:
        odp_bytes = f.read()

    if source.suffix == ".svg":
        replace_placeholders(source, data)
        output_file = source.parent / source

    if source.suffix == ".pptx":
        unpack_dir = unpack(odp_bytes, source.name)

        slide_dir = unpack_dir / 'ppt' / 'slides'
        if slide_dir.exists():
            for xml_file in slide_dir.glob('*.xml'):
                replace_placeholders(xml_file, data)

        output_file = unpack_dir.parent / f"{source.stem}.pptx"
        pack_pptx(unpack_dir, output_file)

    if source.suffix == ".odp":
        unpack_dir = unpack(odp_bytes, source.name)

        content_xml = unpack_dir / "content.xml"
        replace_placeholders(content_xml, data)

        output_file = unpack_dir.parent / f"{source.stem}.odp"
        pack_odp(unpack_dir, output_file)
    return output_file