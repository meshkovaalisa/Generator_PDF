import json
from office_templates.office_renderer import render_pptx

# Загружаем данные
with open('data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Самый простой вызов
render_pptx('test.pptx', data, 'result.pptx', check_permissions=lambda x:x)

print("✅ Готово!")