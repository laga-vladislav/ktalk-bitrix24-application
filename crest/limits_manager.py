from functools import wraps
from datetime import timedelta, datetime, timezone
import json


class LimitsManager:
    def __init__(
            self) -> None:
        pass

    def __call__(self, func):
        @wraps(func)
        async def func_wrapper(*args, **kwargs):
            response = await func(*args, **kwargs)

            print("Limits manager here")
            if not self.is_batch(response=response):
                method = kwargs['request'].method if kwargs else None
                operating = response["time"]["operating"]
            else:
                print(args)
                result_time = response["result"]["result_time"]
                first_request_key = next(iter(result_time))
                operating = result_time[first_request_key]['operating']
            print(operating)
            return response

        return func_wrapper

    def is_batch(self, response: dict) -> bool:
        if isinstance(response["result"], int):
            return False
        return True
