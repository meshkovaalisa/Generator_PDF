import re


def clear_html(item_data: dict):
    for field in list(item_data.keys()):
        if isinstance(item_data[field], dict) and "TEXT" in item_data[field]:
            html_text = item_data[field]["TEXT"]
            html_text = re.sub(r'<li[^>]*>', '\n• ', html_text)
            html_text = re.sub(r'</li>', '', html_text)
            html_text = re.sub(r'<p[^>]*>', '\n', html_text)
            html_text = re.sub(r'</p>', '', html_text)
            html_text = re.sub(r'<br\s*/?>', '\n', html_text)
            html_text = re.sub(r'</?(?:ul|ol|div|span|strong|em|b|i)[^>]*>', '', html_text)
            html_text = re.sub(r'<[^>]+>', '', html_text)
            html_text = html_text.replace('&nbsp;', ' ')
            html_text = html_text.replace('&amp;', '&')
            html_text = html_text.replace('&lt;', '<')
            html_text = html_text.replace('&gt;', '>')
            html_text = html_text.replace('&quot;', '"')
            html_text = re.sub(r'\n\s*\n', '\n', html_text)
            html_text = re.sub(r'^\s+', '', html_text, flags=re.MULTILINE)
            html_text = re.sub(r'[ \t]+\n', '\n', html_text)
            html_text = html_text.strip()
            item_data[field] = html_text
    return item_data


def filter_data(item_data: dict):
    new_item_data = dict()

    # Удаление полей для разных уровней образования
    if item_data.get("education") in ["Аспирантура", "Магистратура"]:
        for key in ["VI_1", "VI_2", "VI_3_choice_1", "VI_3_choice_2", "VI_3_choice_3"]:
            item_data.pop(key, None)

    if item_data.get("education") in ["Специалитет", "Бакалавриат"]:
        item_data.pop("VI_mag_asp", None)

    # ========== ГЛАВНОЕ: ДОБАВЛЯЕМ ПОЛЯ ДЛЯ ЕГЭ ==========
    # Основные экзамены
    item_data["V1_1"] = item_data.get("VI_1", "—")
    item_data["V1_2"] = item_data.get("VI_2", "—")

    # Экзамены на выбор
    item_data["V1_3"] = item_data.get("VI_3_choice_1", "—")
    item_data["V1_4"] = item_data.get("VI_3_choice_2", "—")
    item_data["V1_5"] = item_data.get("VI_3_choice_3", "—")

    # Если основные пустые, но есть массив VI
    if item_data["V1_1"] == "—" and "VI" in item_data and isinstance(item_data["VI"], list):
        if len(item_data["VI"]) > 0 and item_data["VI"][0]:
            item_data["V1_1"] = item_data["VI"][0]
        if len(item_data["VI"]) > 1 and item_data["VI"][1]:
            item_data["V1_2"] = item_data["VI"][1]

    # Если экзамены на выбор пустые, но есть массив VI_choice
    if item_data["V1_3"] == "—" and "VI_choice" in item_data and isinstance(item_data["VI_choice"], list):
        choices = [ex for ex in item_data["VI_choice"] if ex]
        for i, choice in enumerate(choices[:3]):
            item_data[f"V1_{i + 3}"] = choice
    # ===================================================

    # Поля opp1..opp5 (из work)
    work_text = ""
    if "work" in item_data:
        if isinstance(item_data["work"], dict) and "TEXT" in item_data["work"]:
            work_text = item_data["work"]["TEXT"]
        else:
            work_text = str(item_data["work"])

    work_text = re.sub(r'<[^>]+>', '', work_text)
    lines = [l.strip() for l in work_text.split('\n') if l.strip()]
    opportunities = []
    for line in lines:
        if line.startswith(('•', '-', '*', '—')):
            opportunities.append(re.sub(r'^[•\-*—]\s*', '', line))
        else:
            opportunities.append(line)

    while len(opportunities) < 5:
        opportunities.append("")

    for i in range(1, 6):
        item_data[f"opp{i}"] = opportunities[i - 1]

    # Поля study1..study8 (из study)
    study_text = ""
    if "study" in item_data:
        if isinstance(item_data["study"], dict) and "TEXT" in item_data["study"]:
            study_text = item_data["study"]["TEXT"]
        else:
            study_text = str(item_data["study"])

    study_text = re.sub(r'<[^>]+>', '', study_text)
    study_lines = [l.strip() for l in study_text.split('\n') if l.strip()]
    study_items = []
    for line in study_lines:
        if line.startswith(('•', '-', '*', '—')):
            study_items.append(re.sub(r'^[•\-*—]\s*', '', line))
        elif re.match(r'^\d+\.', line):
            study_items.append(re.sub(r'^\d+\.\s*', '', line))
        else:
            study_items.append(line)

    while len(study_items) < 8:
        study_items.append("")

    for i in range(1, 9):
        item_data[f"study{i}"] = study_items[i - 1]

    # profile_value
    item_data["profile_value"] = item_data.get("specialty", "Не указано")

    # budget_or_paid_str
    if "budget_or_paid" in item_data and isinstance(item_data["budget_or_paid"], list):
        item_data["budget_or_paid_str"] = ", ".join(item_data["budget_or_paid"])
    else:
        item_data["budget_or_paid_str"] = item_data.get("budget_or_paid", "Информация отсутствует")

    # Обработка title
    parts = item_data["title"].split(". ")
    if len(parts) != 2 and "(с двумя профилями подготовки)" not in item_data["title"]:
        parts = item_data["title"].rsplit(".", 1)

    item_data.pop("title", None)

    new_item_data["code_program"] = parts[0]
    new_item_data["program"] = ". ".join(parts[1:]) if len(parts) > 1 else ""
    if len(new_item_data["code_program"]) < 10:
        new_item_data["code_program"] = ". ".join(parts[0:])
        new_item_data["program"] = ""

    new_item_data.update(item_data)
    clear_html(new_item_data)

    return new_item_data