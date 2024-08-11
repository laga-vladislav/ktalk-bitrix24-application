from json import JSONDecodeError
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
            raise ValueError("Необходимо задать client_id и client_secret, либо client_webhook")
        
        self.CLIENT_WEBHOOK = client_webhook
        self.CLIENT_ID = client_id
        self.CLIENT_SECRET = client_secret
        self.BATCH_SIZE = batch_size

    async def call(self, request: CallRequest, client_endpoint: str = "", auth_token: str = "") -> Any:
        '''
        Выполняет запрос к Bitrix24
        Происходит проверка, какой режим активирован, и выставляется соответственный адрес
        
        :param request: Объект CallRequest (запрос)
        :return: Ответ Bitrix24
        '''
        if self.mode == "webhook":
            request.domain = self.CLIENT_WEBHOOK
        elif self.mode == "application":   
            request.domain = client_endpoint
            request.params["auth"] = auth_token

        response = await self._call_curl(request)
        return response

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
            response = await self.call(batch_CallRequest)
            responses.append(response)

        return responses

    async def _call_curl(self, request: CallRequest) -> Any:
        """
        Выполняет запрос к Bitrix24 по указанному адресу и методу.

        :param request: Объект CallRequest, содержащий информацию о запросе.
        :return: возвращает ответ от Bitrix24 в формате json.
        """
        url = request.get_full_url()
        try:
            async with AsyncClient() as client:
                response = await client.post(url=url)
                
                response.raise_for_status()
                return response.json()
                    
        except JSONDecodeError:
            # НАПИСАТЬ ТУТ придумаать ошибку чо как и почему
            return response


    async def refresh_token(self, refresh_token: str):
        """
        Метод обновляет токен авторизации. Работает только для приложений.

        :param refresh_token: значение сохраненного токена продления авторизации.
        :return: ответ от сервера в формате JSON.
        """
        if self.mode != "application":
            raise ValueError("Метод доступен только для приложений")

        # URL для запроса обновления токена
        url = "https://oauth.bitrix.info/oauth/token/"
        payload = {
            "grant_type": "refresh_token",  # тип авторизационных данных
            "client_id": self.CLIENT_ID,  # код приложения
            "client_secret": self.CLIENT_SECRET,  # секретный ключ приложения
            "refresh_token": refresh_token  # значение сохраненного токена продления авторизации
        }

        callRequest = CallRequest(domain=url, params=payload)
        
        response = await self._call_curl(callRequest)
        return(response)
    
    async def get_auth(self, code: str):
        """
        Метод выдает данные авторизации. Работает только для приложений.
        Выдает и refresh_token, и access_token.

        :param code: код для получения авторизационных данных.
        :return: ответ от сервера в формате JSON.
        """
        if self.mode != "application":
            raise ValueError("Метод доступен только для приложений")

        # URL для запроса обновления токена
        url = "https://oauth.bitrix.info/oauth/token/"
        payload = {
            "grant_type": "authorization_code",  # тип авторизационных данных
            "client_id": self.CLIENT_ID,  # код приложения
            "client_secret": self.CLIENT_SECRET,  # секретный ключ приложения
            "code": code  # код для получения токена
        }

        callRequest = CallRequest(domain=url, params=payload)
        
        response = await self._call_curl(callRequest)
        return(response)