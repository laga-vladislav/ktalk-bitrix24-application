from httpx import AsyncClient, HTTPStatusError
from typing import Any
from crest.models import CallRequest, AuthTokens
from crest.limits_manager import LimitsManager


class CRestBitrix24:
    limits_manager = LimitsManager()

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
        auth_tokens: AuthTokens = None,
    ) -> Any:
        if self.mode == "webhook":
            client_endpoint = self.CLIENT_WEBHOOK
        elif self.mode == "application" and not auth_tokens:
            raise ValueError(
                "В режиме работы с приложениями необходимо задать токены доступа"
            )
        elif self.mode == "application" and not client_endpoint:
            raise ValueError(
                "В режиме работы с приложениями необходимо задать client_endpoint"
            )

        response = await self._call_curl(request, client_endpoint, auth_tokens)
        return response

    async def call_batch(
        self,
        request_batch: list[CallRequest],
        halt: bool = False,
        client_endpoint: str = None,
        auth_tokens: AuthTokens = None,
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
                parameters["cmd"][f"request{
                    index}"] = request_batch[index].get_path()

            # Назначение параметров запроса и отправка
            batch_CallRequest.params = parameters
            response = await self.call(batch_CallRequest, client_endpoint, auth_tokens)
            responses.append(response)

        return responses

    @limits_manager
    async def _call_curl(
        self, request: CallRequest, client_endpoint: str, auth_tokens: AuthTokens = None
    ) -> Any:
        copy_request = request.model_copy()

        if auth_tokens:
            copy_request.params["auth"] = auth_tokens.access_token

        async def perform_request():
            url = client_endpoint + copy_request.get_path()

            async with AsyncClient() as client:
                response = await client.post(url=url)
                response.raise_for_status()
                return response.json()

        try:
            return await perform_request()

        except HTTPStatusError as e:
            if e.response.status_code == 414:
                raise HTTPStatusError('Слишком длинный URI')
            elif e.response.json().get("error") == "expired_token":
                new_auth = await self.refresh_token(
                    refresh_token=auth_tokens.refresh_token
                )
                auth_tokens.access_token = new_auth["access_token"]
                auth_tokens.refresh_token = new_auth["refresh_token"]

                copy_request.params["auth"] = auth_tokens.access_token
                return await perform_request()
            else:
                return e.response.json()

    async def refresh_token(self, refresh_token: str):
        if self.mode != "application":
            raise ValueError("Метод доступен только для приложений")

        # URL для запроса обновления токена
        url = "https://oauth.bitrix.info/oauth/token/"
        payload = {
            "grant_type": "refresh_token",  # тип авторизационных данных
            "client_id": self.CLIENT_ID,  # код приложения
            "client_secret": self.CLIENT_SECRET,  # секретный ключ приложения
            # значение сохраненного токена продления авторизации
            "refresh_token": refresh_token,
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
