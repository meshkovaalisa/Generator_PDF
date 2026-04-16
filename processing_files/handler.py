import json, os, copy
from collections import defaultdict
from processing_files.modules import unpack, pack_odp, replace_placeholders_in_slide, remove_unmatched_placeholders, \
    random_file_name
from config import temp_dir, faculties_dir
from typing import Dict
from odf.opendocument import load
from odf.draw import Page
import xml.etree.ElementTree as ET


def odp_handler(odp_file_path, data: Dict[str, str], output_file=None):
    """
    Обрабатывает ODP-шаблон, заполняя его данными и возвращая готовый ODP-файл.

    Функция загружает шаблон презентации, обрабатывает его с помощью template_handler,
    распаковывает ODP-файл, заменяет плейсхолдеры в слайдах на фактические данные,
    удаляет неиспользованные плейсхолдеры и упаковывает обратно в ODP-формат.

    Args:
        odp_file_path (Path или str): Путь к файлу-шаблону ODP
        data (Dict[str, str]): Словарь с данными для заполнения слайдов, где ключи -
                               названия факультетов или идентификаторы, значения - данные
        output_file (None, optional): Неиспользуемый параметр для обратной совместимости

    Returns:
        tuple: (output_file_path, unpack_file_path) - кортеж из двух Path объектов:
               - output_file_path: путь к сохранённому ODP-файлу
               - unpack_file_path: путь к временной директории с распакованными файлами
    """
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


def template_handler(template_path, data, output_path=None):
    """
    Создаёт множество копий слайда-шаблона для каждого элемента данных.

    Функция загружает ODP-шаблон, извлекает первый слайд как образец,
    удаляет оригинальный слайд и создаёт его глубокие копии для каждого
    элемента в переданных данных. Сохраняет результат во временный файл.

    Args:
        template_path (Path или str): Путь к файлу-шаблону ODP
        data (list или dict): Данные, количество элементов которых определяет
                              количество создаваемых слайдов
        output_path (None, optional): Неиспользуемый параметр, путь для сохранения

    Returns:
        Path: Путь к сохранённому ODP-файлу с множеством слайдов

    Raises:
        Exception: Если в шаблоне не найдено ни одного слайда
    """
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

    output_path = temp_dir / f"{random_file_name()}.odp"

    template.save(output_path)

    return output_path


def split_by_faculty(data, output_dir=faculties_dir):
    """
    Разбивает список JSON по факультетам и сохраняет в отдельные файлы

    Args:
        data (list): Список JSON объектов, содержащих информацию об образовательных программах
        output_dir (Path или str, optional): Директория для сохранения файлов.
                                             По умолчанию используется faculties_dir из конфигурации

    Returns:
        dict: Словарь, где ключи - названия факультетов, значения - списки JSON объектов,
              принадлежащих соответствующему факультету
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
