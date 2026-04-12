import re

def clear_html(item_data: dict):
    for field in list(item_data.keys()):
        if isinstance(item_data[field], dict) and "TEXT" in item_data[field]:
            html_text = item_data[field]["TEXT"]

            # Шаг 1: Заменяем теги списков на маркеры и переносы
            # <li> → "• " (маркер) + перенос строки
            html_text = re.sub(r'<li[^>]*>', '\n• ', html_text)
            # </li> → убираем
            html_text = re.sub(r'</li>', '', html_text)

            # Шаг 2: Заменяем абзацы на переносы строк
            # <p> → перенос строки
            html_text = re.sub(r'<p[^>]*>', '\n', html_text)
            # </p> → убираем
            html_text = re.sub(r'</p>', '', html_text)

            # Шаг 3: Обрабатываем другие теги
            # <br> → перенос строки
            html_text = re.sub(r'<br\s*/?>', '\n', html_text)
            # <ul>, </ul>, <div> и прочие → просто удаляем
            html_text = re.sub(r'</?(?:ul|ol|div|span|strong|em|b|i)[^>]*>', '', html_text)

            # Шаг 4: Удаляем оставшиеся HTML-теги
            html_text = re.sub(r'<[^>]+>', '', html_text)

            # Шаг 5: Очищаем от &nbsp; и других HTML-сущностей
            html_text = html_text.replace('&nbsp;', ' ')
            html_text = html_text.replace('&amp;', '&')
            html_text = html_text.replace('&lt;', '<')
            html_text = html_text.replace('&gt;', '>')
            html_text = html_text.replace('&quot;', '"')

            # Шаг 6: Нормализуем переносы и пробелы
            # Убираем множественные переносы строк
            html_text = re.sub(r'\n\s*\n', '\n', html_text)
            # Убираем пробелы в начале строк
            html_text = re.sub(r'^\s+', '', html_text, flags=re.MULTILINE)
            # Убираем пробелы перед переносами
            html_text = re.sub(r'[ \t]+\n', '\n', html_text)
            # Финальная очистка пробелов
            html_text = html_text.strip()

            item_data[field] = html_text

    return item_data

def filter_data(item_data: dict):
    new_item_data = dict()
    try:
        if (item_data.get("education") == "Аспирантура") or (item_data.get("education") == "Магистратура"):
            for key in ["VI_1", "VI_2", "VI_3_choice_1", "VI_3_choice_2", "VI_3_choice_3"]:
                item_data.pop(key, None)

        if (item_data.get("education") == "Специалитет") or (item_data.get("education") == "Бакалавриат"):
            for key in ["VI_mag_asp"]:
                item_data.pop(key, None)
    finally:
        for key in ["id", "created_at", "updated_at", "city", "average_score", "special_quota", "separate_quota", "target_quota", "classifier", "area_of_interest",
                    "VI", "VI_choice", "profile_exam_1", "profile_exam_2", "profile_exam_choice_1", "profile_exam_choice_2", "profile_exam_choice_3",
                    "profile_exam_choice_4", "partners", "optional", "classifier", "area_of_interest", "specialty", "program_card", "VI_3_choice_4"]:
            item_data.pop(key, None)
        parts = item_data["title"].split(". ")

        if len(parts) != 2 and "(с двумя профилями подготовки)" not in item_data["title"]:
            parts = item_data["title"].rsplit(".", 1)

        item_data.pop("title", None)

        new_item_data["code_program"] = parts[0]
        new_item_data["program"] = ". ".join(parts[1:])
        if len(new_item_data["code_program"]) < 10:
            new_item_data["code_program"] = ". ".join(parts[0:])
            new_item_data["program"] = ""
        new_item_data.update(item_data)

        # for field in ["work", "about", "study"]:
        #     if "TEXT" in new_item_data[field]:
        #         # Удаляем HTML-теги
        #         clean_text = re.sub(r'<[^>]+>', '', new_item_data[field]["TEXT"])
        #         # Нормализуем пробелы и переносы
        #         clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        #         # Заменяем словарь на простую строку
        #         new_item_data[field] = clean_text

        clear_html(new_item_data)

    return new_item_data




