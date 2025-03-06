import collections
from functools import wraps
from datetime import timedelta, datetime, timezone
import json


class LimitsManager:
    def __init__(self) -> None:
        self._request_history = collections.deque()

    def __call__(self, func):
        @wraps(func)
        async def func_wrapper(*args, **kwargs):
            response = await func(*args, **kwargs)
            print("Limits manager here")
            method, operating = self._get_data_from_args(args, response)

            print(f"Method '{method}' has operating {operating}")
            return response

        return func_wrapper

    def _get_data_from_args(self, args, response) -> tuple:
        method = None
        operating = None
        if not self._is_batch(response=response):
            try:
                method = args[1].method if args else None
                operating = response["time"]["operating"]
            except:
                pass
        else:
            # print(f"Args: {args}, kwargs: {kwargs}")
            result_time = response["result"]["result_time"]
            first_request_key = next(iter(result_time))
            operating = result_time[first_request_key]['operating']
        return method, operating

    def _is_batch(self, response: dict) -> bool:
        try:  # обрабатываем ситуации, где нет ответа с результатом. Например, refresh_token
            # у батча данная запись - словарь
            if isinstance(response["result"], int):
                return False
            return True
        except:
            return False
