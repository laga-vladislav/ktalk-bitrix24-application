from httpx import AsyncClient
from typing import Any
from crest.models import CallRequest


class CRestBitrix24:
    def __init__(
        self,
        client_webhook: str | None,
        client_id: str | None,
        client_secret: str | None,
        batch_size: int = 50,
    ) -> None:
        if not (client_id and client_secret) and not client_webhook:
            raise ValueError(
                "Необходимо задать client_webhook, либо client_id и client_secret"
            )
        self.CLIENT_WEBHOOK = client_webhook
        self.CLIENT_ID = client_id
        self.CLIENT_SECRET = client_secret
        self.BATCH_SIZE = batch_size

    async def call(self, request: CallRequest) -> Any:
        '''
        Выполняет запрос к Bitrix24
        
        :param request: Объект CallRequest (запрос)
        :return: Ответ Bitrix24
        '''
        return await self._call_curl(request)

    async def call_batch(self, request_batch: list[CallRequest], halt=False):
        '''
        Выполняет пакетный запрос к Bitrix24
        
        :param request_batch: Список объектов CallRequest (массив запросов)
        :param halt: Определяет прерывать ли последовательность запросов в случае ошибки
        :return: список ответов Bitrix24
        '''
        responses = []

        batch_size = self.BATCH_SIZE
        total_requests = len(request_batch)

        for start in range(0, total_requests, batch_size):
            # пакет с методом batch
            batch_CallRequest = CallRequest(method="batch")
            parameters = {"halt": int(halt), "cmd": {}}

            # Добавляем параметры в пакет выше
            for count in range(batch_size):
                index = start + count
                if index >= total_requests:
                    break
                parameters["cmd"][f"request{index}"] = request_batch[index].get_path()

            # Назначение параметров запроса и отправка
            batch_CallRequest.params = parameters
            response = await self._call_curl(batch_CallRequest)
            responses.append(response)

        return responses

    async def _call_curl(self, request: CallRequest) -> Any:
        url = f"{self.CLIENT_WEBHOOK}/{request.get_path()}"

        async with AsyncClient() as client:
            response = await client.post(url=url)
            return response.json()


# async def refresh_token(client_id, client_secret, refresh_token):
#     """
#     Метод обновляет токен авторизации.

#     :param client_id: код приложения, получаемый в партнерском кабинете при регистрации приложения
#                       либо на портале в случае локального приложения.
#     :param client_secret: секретный ключ приложения, получаемый в партнерском кабинете при регистрации
#                           приложения либо на портале в случае локального приложения.
#     :param refresh_token: значение сохраненного токена продления авторизации.
#     :return: ответ от сервера в формате JSON.
#     """
#     # URL для запроса обновления токена
#     url = "https://oauth.bitrix.info/oauth/token/"
#     payload = {
#         "grant_type": "refresh_token",  # тип авторизационных данных
#         "client_id": client_id,  # код приложения
#         "client_secret": client_secret,  # секретный ключ приложения
#         "refresh_token": refresh_token  # значение сохраненного токена продления авторизации
#     }
#     async with AsyncClient() as client:
#         response = client.post(url, data=payload)
#         return response.json()
