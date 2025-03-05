import json

from src.logger.custom_logger import logger

from fastapi import Request, HTTPException, Response
from starlette.middleware.base import BaseHTTPMiddleware

from src.auth import verify_token
from src.middleware.utils import parse_form_data


class JWTAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            # Исключения для публичных роутов
            if request.url.path in ["/docs", "/redoc"] or request.url.path.startswith("/openapi") or request.url.path in ["/handler", "/ktalk-robot", "/install", "/placement"]:
                return await call_next(request)

            logger.debug(request.headers)
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                raise HTTPException(
                    status_code=401, detail="Missing or invalid Authorization header")

            token = auth_header.split("Bearer ")[-1]
            if not verify_token(token):
                raise HTTPException(
                    status_code=401, detail="Invalid or expired token")

            return await call_next(request)

        except HTTPException as e:
            return Response(content=e.detail, status_code=e.status_code)


class LogRequestDataMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        raw_body = await request.body()

        logger_message = []

        # Выводим метод запроса и URL
        logger_message.append(
            f"Поступил {request.method} запрос на {request.url.path}")
        logger_message.append(f"URL: {request.url}")

        # Выводим заголовки в формате JSON
        headers = dict(request.headers)

        headers_json = json.dumps(headers, indent=4, ensure_ascii=False)
        logger_message.append(f"Заголовки запроса:\n{headers_json}")

        # Выводим параметры запроса
        query_params = dict(request.query_params)

        query_params_json = json.dumps(
            query_params, indent=4, ensure_ascii=False)
        logger_message.append(f"Параметры запроса:\n{query_params_json}")

        # Тип содержимого тела запроса
        content_type = request.headers.get("content-type")
        body = {}

        # Если тело запроса в формате JSON
        if content_type == "application/json":
            body = await request.json()

            body_json = json.dumps(body, indent=4, ensure_ascii=False)
            logger_message.append(f"Тело запроса (JSON):\n{body_json}\n")

        # Если тело запроса в формате Form Data
        elif content_type == "application/x-www-form-urlencoded":
            body = await request.form()
            body = dict(body)
            body = parse_form_data(body)

            form_data_json = json.dumps(body, indent=4, ensure_ascii=False)
            logger_message.append(
                f"Тело запроса (Form Data):\n{form_data_json}\n")

        else:
            logger_message.append(f"Тело запроса:\n{body}\n")

        # Логирование информации о запросе
        logger.debug("\n".join(logger_message))
        logger_message = []

        # Сохранение информации о запросе
        request.state.headers = headers
        request.state.query_params = query_params
        request.state.body = body

        request._body = raw_body
        # Передача запроса обработчику
        response = await call_next(request)

        # Логирование информации об ответе
        logger_message.append(f"Ответ на запрос {request.url.path}")
        logger_message.append(f"Статус ответа: {response.status_code}")
        response_headers = dict(response.headers)
        response_headers_json = json.dumps(
            response_headers, indent=4, ensure_ascii=False
        )
        logger_message.append(f"Заголовки ответа:\n{response_headers_json}")

        # Логирование информации о запросе
        logger.debug("\n".join(logger_message))
        logger_message = []

        return response
