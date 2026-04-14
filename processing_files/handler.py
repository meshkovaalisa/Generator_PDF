import json, os, copy
from collections import defaultdict
from processing_files.modules import unpack, pack_odp, replace_placeholders_in_slide, remove_unmatched_placeholders, random_file_name
from config import temp_dir, faculties_dir
from typing import Dict
from odf.opendocument import load
from odf.draw import Page
import xml.etree.ElementTree as ET

def odp_handler(odp_file_path, data: Dict[str, str], output_file = None):

    main_odp_path = template_handler(odp_file_path, data)

    with open(main_odp_path, 'rb') as f:
        odp_bytes = f.read()


    unpack_file_path = unpack(odp_bytes, main_odp_path)

    content_xml = unpack_file_path / "content.xml"

    namespaces = {
        'office': 'urn:oasis:names:tc:opendocument:xmlns:office:1.0',
        'draw': 'urn:oasis:names:tc:opendocument:xmlns:drawing:1.0'
    }

    tree = ET.parse(content_xml)
    root = tree.getroot()

    slides = root.findall('.//draw:page', namespaces)

    for idx, slide in enumerate(slides[:len(data)]):
        print(f"Обработка слайда {idx + 1} с данными: {data[idx]}")

        replace_placeholders_in_slide(slide, data[idx])
        used_keys = data[idx].keys()
        remove_unmatched_placeholders(slide, used_keys)


    tree.write(content_xml, encoding='utf-8', xml_declaration=True)

    output_file_path = unpack_file_path.parent / f"{main_odp_path.stem}.odp"
    pack_odp(unpack_file_path, output_file_path)

    return output_file_path, unpack_file_path

def template_handler(template_path, data, output_path = None):

    template = load(template_path)

    slides = template.presentation.getElementsByType(Page)
    if not slides:
        raise Exception("В шаблоне не найдено ни одного слайда.")
    template_slide = slides[0]

    # Удаляем исходный слайд
    template.presentation.removeChild(template_slide)

    # Создаем слайды для каждого набора данных
    for _ in enumerate(data):
        new_slide = copy.deepcopy(template_slide)

        template.presentation.addElement(new_slide)

    output_path = temp_dir/ f"{random_file_name()}.odp"

    template.save(output_path)

    return output_path

def split_by_faculty(data, output_dir=faculties_dir):
    """
    Разбивает список JSON по факультетам и сохраняет в отдельные файлы

    Args:
        data: список JSON объектов
        output_dir: директория для сохранения файлов
    """

    os.makedirs(output_dir, exist_ok=True)

    faculty_groups = defaultdict(list)

    for item in data:
        faculty = item.get("faculty", "unknown")
        faculty_groups[faculty].append(item)

    # Сохраняем каждую группу в отдельный JSON файл
    for faculty, items in faculty_groups.items():
        # Формируем имя файла
        filename = f"{faculty}.json"
        # Очищаем имя от недопустимых символов
        filepath = f"{output_dir}/{filename}" if output_dir != "." else filename

        # Сохраняем JSON
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(items, f, ensure_ascii=False, indent=2)

        print(f"✅ Создан {filename}: {len(items)} записей")

    return dict(faculty_groups)
