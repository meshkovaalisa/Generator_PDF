import re
from typing import Dict, Any, List, Tuple, Union

# регулярки
RE_LI_OPEN = re.compile(r'<li[^>]*>')
RE_LI_CLOSE = re.compile(r'</li>')
RE_P_OPEN = re.compile(r'<p[^>]*>')
RE_P_CLOSE = re.compile(r'</p>')
RE_BR = re.compile(r'<br\s*/?>')
RE_INLINE_TAGS = re.compile(r'</?(?:ul|ol|div|span|strong|em|b|i)[^>]*>')
RE_ALL_TAGS = re.compile(r'<[^>]+>')
RE_MULTIPLE_NEWLINES = re.compile(r'\n\s*\n')
RE_LINE_START_SPACES = re.compile(r'^\s+', flags=re.MULTILINE)
RE_SPACES_BEFORE_NEWLINE = re.compile(r'[ \t]+\n')
RE_BULLET = re.compile(r'^[•\-*—]\s*')
RE_NUMBERED = re.compile(r'^\d+\.\s*')

BULLET_MARKERS = ('•', '-', '*', '—')

HTML_ENTITIES = {
    '&nbsp;': ' ',
    '&amp;': '&',
    '&lt;': '<',
    '&gt;': '>',
    '&quot;': '"',
}


def clean_html_text(html_text: str) -> str:
    """Очистка HTML-текста"""
    html_text = RE_LI_OPEN.sub('\n• ', html_text)
    html_text = RE_LI_CLOSE.sub('', html_text)
    html_text = RE_P_OPEN.sub('\n', html_text)
    html_text = RE_P_CLOSE.sub('', html_text)
    html_text = RE_BR.sub('\n', html_text)
    html_text = RE_INLINE_TAGS.sub('', html_text)
    html_text = RE_ALL_TAGS.sub('', html_text)

    for entity, replacement in HTML_ENTITIES.items():
        html_text = html_text.replace(entity, replacement)

    html_text = RE_MULTIPLE_NEWLINES.sub('\n', html_text)
    html_text = RE_LINE_START_SPACES.sub('', html_text)
    html_text = RE_SPACES_BEFORE_NEWLINE.sub('\n', html_text)

    return html_text.strip()


def clear_html(item_data: Dict[str, Any]) -> Dict[str, Any]:
    """Очистка HTML в полях словаря"""
    for field, value in item_data.items():
        if isinstance(value, dict) and "TEXT" in value:
            item_data[field] = clean_html_text(value["TEXT"])
    return item_data


def parse_bullet_list(text: str, max_items: int) -> List[str]:
    """Извлечение элементов списка из текста с маркерами"""
    text = RE_ALL_TAGS.sub('', text)
    lines = [line.strip() for line in text.split('\n') if line.strip()]

    items = []
    for line in lines:
        if line.startswith(BULLET_MARKERS):
            items.append(RE_BULLET.sub('', line))
        elif RE_NUMBERED.match(line):
            items.append(RE_NUMBERED.sub('', line))
        else:
            items.append(line)

    items.extend([''] * (max_items - len(items)))
    return items[:max_items]


def get_text_field(item_data: Dict[str, Any], field_name: str) -> str:
    """Получение текстового поля"""
    field = item_data.get(field_name, "")
    if isinstance(field, dict):
        return field.get("TEXT", "")
    return str(field)


def handle_ege_exams(item_data: Dict[str, Any]) -> None:
    """Обработка полей ЕГЭ"""
    vi = item_data.get("VI")
    vi_1 = item_data.get("VI_1")
    vi_2 = item_data.get("VI_2")

    item_data["V1_1"] = vi_1 if vi_1 else "—"
    item_data["V1_2"] = vi_2 if vi_2 else "—"

    if item_data["V1_1"] == "—" and isinstance(vi, list):
        if len(vi) > 0 and vi[0]:
            item_data["V1_1"] = vi[0]
        if len(vi) > 1 and vi[1]:
            item_data["V1_2"] = vi[1]

    vi_choices = [item_data.get(f"VI_3_choice_{i}") for i in range(1, 4)]
    all_empty = True

    for i in range(3):
        value = vi_choices[i]
        item_data[f"V1_{i + 3}"] = value if value else "—"
        if value:
            all_empty = False

    if all_empty and isinstance(item_data.get("VI_choice"), list):
        choices = [ex for ex in item_data["VI_choice"] if ex]
        for i, choice in enumerate(choices[:3]):
            item_data[f"V1_{i + 3}"] = choice


def split_title(title: str) -> Tuple[str, str]:
    parts = title.split(". ")
    if len(parts) != 2 and "(с двумя профилями подготовки)" not in title:
        parts = title.rsplit(".", 1)

    if parts:
        code = parts[0]
        program = ". ".join(parts[1:]) if len(parts) > 1 else ""

        if len(code) < 10:
            code = ". ".join(parts)
            program = ""

        return code, program

    return title, ""


def filter_data(item_data: Dict[str, Any]) -> Dict[str, Any]:
    """Фильтрация и преобразование данных"""
    education = item_data.get("education", "")

    if education in ("Аспирантура", "Магистратура"):
        for key in ("VI_1", "VI_2", "VI_3_choice_1", "VI_3_choice_2", "VI_3_choice_3"):
            item_data.pop(key, None)
    elif education in ("Специалитет", "Бакалавриат"):
        item_data.pop("VI_mag_asp", None)

    handle_ege_exams(item_data)

    work_text = get_text_field(item_data, "work")
    opportunities = parse_bullet_list(work_text, 5)
    for i, opp in enumerate(opportunities, 1):
        item_data[f"opp{i}"] = opp

    study_text = get_text_field(item_data, "study")
    study_items = parse_bullet_list(study_text, 8)
    for i, item in enumerate(study_items, 1):
        item_data[f"study{i}"] = item

    item_data["profile_value"] = item_data.get("specialty", "Не указано")

    budget = item_data.get("budget_or_paid")
    if isinstance(budget, list):
        item_data["budget_or_paid_str"] = ", ".join(budget)
    else:
        item_data["budget_or_paid_str"] = budget if budget else "Информация отсутствует"

    title = item_data.pop("title", "")
    code, program = split_title(title)

    new_item_data = {
        "code_program": code,
        "program": program
    }

    new_item_data.update(item_data)
    clear_html(new_item_data)

    return new_item_data