import re


def get_offset_sec(gmt_timezone: str) -> int:
    match = re.match(r'GMT([+-]?\d+)', gmt_timezone)
    if not match:
        raise ValueError("Неверный GMT формат")
    offset_hours = int(match.group(1))
    return offset_hours * 3600
