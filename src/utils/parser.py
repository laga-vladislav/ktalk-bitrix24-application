import json
import re

def parse_form_data(form_data):
    parsed_data = {}
    
    for key, value in form_data.items():
        keys = [k for k in re.split(r'\[|\]', key) if k]  # Удаляем пустые ключи
        current_level = parsed_data
        
        for i, k in enumerate(keys):
            if i == len(keys) - 1:
                # Последний элемент, устанавливаем значение
                current_level[k] = convert_value(value)
            else:
                # Если ключа нет, создаем словарь
                if k not in current_level:
                    current_level[k] = {}
                current_level = current_level[k]
    
    return parsed_data

def convert_value(value):
    # Преобразуем значение в тип данных, если это возможно
    try:
        # Попытка преобразовать строку в JSON
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        # Возвращаем значение как есть, если оно не является JSON
        return value