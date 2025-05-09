from datetime import datetime


def date_validator(date_value: str | int) -> str | int:
    if isinstance(date_value, int) or (isinstance(date_value, str) and date_value.isdigit()):
        timestamp = int(date_value)
        timestamp_sec = timestamp // 1000
        datetime.fromtimestamp(timestamp_sec)  # Проверка корректности
        return timestamp
    else:
        try:
            datetime.strptime(date_value, '%d.%m.%Y %H:%M:%S')
            return date_value
        except ValueError:
            try:
                datetime.strptime(date_value, '%Y-%m-%dT%H:%M:%SZ')
                return date_value
            except ValueError:
                raise ValueError(
                    "Дата должна быть в формате timestamp, 'dd.mm.yyyy HH:MM:SS', '%Y-%m-%dT%H:%M:%SZ'")


def timezone_validator(timezone_value: str) -> str:
    timezone_value = timezone_value.upper()
    if 'GMT' not in timezone_value:
        raise ValueError("Часовой пояс должен начинаться с 'GMT'")
    elif '+' not in timezone_value and '-' not in timezone_value:
        raise ValueError("Часовой пояс должен содержать '+' или '-'")
    elif timezone_value.count('+') > 1 or timezone_value.count('-') > 1:
        raise ValueError(
            "Часовой пояс должен содержать только один знак '+' или '-'")
    else:
        try:
            int(timezone_value.split('+')[1]) if '+' in timezone_value else int(timezone_value.split('-')[1])
        except ValueError:
            raise ValueError("Часовой пояс должен содержать цифры")
    return timezone_value


def pincode_validator(pinCode_value: str | int) -> str | int:
    if isinstance(pinCode_value, int):
        pinCode_value = str(pinCode_value)
    else:
        if pinCode_value == "":
            return pinCode_value
        try:
            int(pinCode_value)
        except ValueError:
            raise ValueError("Пин код должен содержать только цифры")
    if any((len(pinCode_value) < 4, len(pinCode_value) > 6)):
        raise ValueError("Пин код должен содержать от 4 до 6 цифр")
    return pinCode_value


def bool_validator(value: bool | str) -> bool | str:
    if isinstance(value, str):
        value = value.upper()
        if value not in ['Y', 'N']:
            raise ValueError(
                "Значение должно быть 'Y' или 'N', либо булевым значением")
        return True if value == 'Y' else False
    return value
