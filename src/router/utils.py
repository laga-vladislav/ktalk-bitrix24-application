from datetime import datetime, timedelta
from fastapi import Request
from crest.crest import CRestBitrix24


def get_crest(request: Request) -> CRestBitrix24:
    return request.app.state.CRest


def format_timezone_from_offset(msk_offset_hours: int, prefix: str = "GMT") -> str:
    """
    Возвращает часовой пояс формата GMT, получает разницу от МСК
    """
    gmt_offset = 3 + msk_offset_hours
    sign = "+" if gmt_offset >= 0 else "-"
    return f"{prefix}{sign}{abs(gmt_offset)}"
