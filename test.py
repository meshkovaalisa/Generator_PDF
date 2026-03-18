# Читаем SVG-файл как текст
with open('template.svg', 'r', encoding='utf-8') as f:
    template = f.read()

# Данные для подстановки
data = {
    'имя': 'Иван',
    'фамилия': 'Иванов',
    'номер': '12345',
    'дата': '18.03.2026'
}

# Выполняем подстановку
result = template.format(**data)

# Сохраняем результат
with open('result.svg', 'w', encoding='utf-8') as f:
    f.write(result)