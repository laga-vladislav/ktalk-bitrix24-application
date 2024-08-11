from httpx import AsyncClient
from typing import Any
from crest.models import CallRequest


class CRestBitrix24:
    def __init__(
        self,
        client_webhook: str | None = None,
        client_id: str | None = None,
        client_secret: str | None = None,
        batch_size: int = 50,
    ) -> None:
        if client_id and client_secret:
            self.mode = "application"
        elif client_webhook:
            self.mode = "webhook"
        else:
            raise ValueError(
                "Необходимо задать client_id и client_secret, либо client_webhook"
            )

        self.CLIENT_WEBHOOK = client_webhook
        self.CLIENT_ID = client_id
        self.CLIENT_SECRET = client_secret
        self.BATCH_SIZE = batch_size

    async def call(
        self,
        request: CallRequest,
        client_endpoint: str = None,
        access_token: str = None,
    ) -> Any:
        if self.mode == "webhook":
            client_endpoint = self.CLIENT_WEBHOOK
        elif self.mode == "application" and not access_token:
            raise ValueError(
                "В режиме работы с приложениями необходимо задать access_token"
            )
        elif self.mode == "application" and not client_endpoint:
            raise ValueError(
                "В режиме работы с приложениями необходимо задать client_endpoint"
            )

        response = await self._call_curl(request, client_endpoint, access_token)
        return response

    async def call_batch(
        self,
        request_batch: list[CallRequest],
        halt: bool = False,
        client_endpoint: str = None,
        access_token: str = None,
    ) -> Any:
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
            response = await self.call(batch_CallRequest, client_endpoint, access_token)
            responses.append(response)

        return responses

    async def _call_curl(
        self, request: CallRequest, client_endpoint: str, access_token: str = None
    ) -> Any:
        copy_request = request.model_copy()

        if access_token:
            copy_request.params["auth"] = access_token

        url = client_endpoint + copy_request.get_path()
        try:
            async with AsyncClient() as client:
                response = await client.post(url=url)

                response.raise_for_status()
                return response.json()

        except Exception:
            # НАПИСАТЬ ТУТ придумаать ошибку чо как и почему
            return response

    async def refresh_token(self, refresh_token: str):
        if self.mode != "application":
            raise ValueError("Метод доступен только для приложений")

        # URL для запроса обновления токена
        url = "https://oauth.bitrix.info/oauth/token/"
        payload = {
            "grant_type": "refresh_token",  # тип авторизационных данных
            "client_id": self.CLIENT_ID,  # код приложения
            "client_secret": self.CLIENT_SECRET,  # секретный ключ приложения
            "refresh_token": refresh_token,  # значение сохраненного токена продления авторизации
        }

        callRequest = CallRequest(params=payload)

        response = await self._call_curl(callRequest, client_endpoint=url)
        return response

    async def get_auth(self, code: str):
        if self.mode != "application":
            raise ValueError("Метод доступен только для приложений")

        # URL для запроса получения авторизации
        url = "https://oauth.bitrix.info/oauth/token/"
        payload = {
            "grant_type": "authorization_code",  # тип авторизационных данных
            "client_id": self.CLIENT_ID,  # код приложения
            "client_secret": self.CLIENT_SECRET,  # секретный ключ приложения
            "code": code,  # код для получения токена
        }

        callRequest = CallRequest(params=payload)

        response = await self._call_curl(callRequest, client_endpoint=url)
        return response
