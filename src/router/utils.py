from fastapi import Request
from datetime import datetime
from crest.crest import CRestBitrix24


def get_crest(request: Request) -> CRestBitrix24:
    return request.app.state.CRest


def str_date_to_timestamp_in_millisec(date_str: str, date_format: str = "%Y-%m-%dT%H:%M:%S.%fZ") -> int:
    datetime_value = datetime.strptime(date_str, date_format)
    return int(datetime.timestamp(datetime_value)) * 1000
