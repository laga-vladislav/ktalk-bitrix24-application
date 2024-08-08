import urllib
from httpx import AsyncClient
from typing import Any
from .models import CallRequest


class CRestBitrix24:
    def __init__(
            self,
            client_webhook: str | None,
            client_id: str | None,
            client_secret: str | None) -> None:
        if not (client_id and client_secret) and not client_webhook:
            raise ValueError(
                "Необходимо задать webhook, либо client_id и client_secret")
        self.CLIENT_WEBHOOK = client_webhook
        self.CLIENT_ID = client_id
        self.CLIENT_SECRET = client_secret

    async def call(self, request: CallRequest) -> Any:
        return await self._call_curl(request)

    async def call_batch(self, cmd_batches: list[CallRequest], halt: bool = False) -> Any:
        cmd_batches_copy = cmd_batches.copy()
        count_of_batches = len(cmd_batches_copy) // 50 + 1

        count = 0
        for i in range(count_of_batches):
            CallRequest(
                method="batch",
                params={
                    "halt": halt,
                    "cmd": {
                        f"request{count}": batch.get_path() for batch in cmd_batches_copy[cmd_batches_copy[:50]]
                    }
                }
            )
            cmd_batches_copy = cmd_batches_copy[50:]
            count += 1

    async def _call_curl(self, request: CallRequest) -> Any:
        url = f'{self.CLIENT_WEBHOOK}/{request.get_path()}'

        async with AsyncClient() as client:
            response = await client.post(
                url
            )
            print(response.url)
            return response.json()


async def refresh_token(client_id, client_secret, refresh_token):
    """
    Метод обновляет токен авторизации.

    :param client_id: код приложения, получаемый в партнерском кабинете при регистрации приложения 
                      либо на портале в случае локального приложения.
    :param client_secret: секретный ключ приложения, получаемый в партнерском кабинете при регистрации 
                          приложения либо на портале в случае локального приложения.
    :param refresh_token: значение сохраненного токена продления авторизации.
    :return: ответ от сервера в формате JSON.
    """
    # URL для запроса обновления токена
    url = "https://oauth.bitrix.info/oauth/token/"
    payload = {
        "grant_type": "refresh_token",  # тип авторизационных данных
        "client_id": client_id,  # код приложения
        "client_secret": client_secret,  # секретный ключ приложения
        "refresh_token": refresh_token  # значение сохраненного токена продления авторизации
    }
    async with AsyncClient() as client:
        response = client.post(url, data=payload)
        return response.json()
