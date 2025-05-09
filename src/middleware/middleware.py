import json

from src.logger.custom_logger import logger

from fastapi import Request, HTTPException, Response
from starlette.middleware.base import BaseHTTPMiddleware

from src.auth import verify_token



EXCLUDED_PATHS = {
    "/docs", "/redoc", "/handler", "/create-external-meeting", "/install", "/placement"
}

class JWTAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            try:
                path = request.scope.get("path", "").rstrip("/")
            except Exception:
                path = "/"

            logger.debug(f"METHOD: {request.method}, PATH: {path}")
            logger.debug(f"HEADERS: {dict(request.headers)}")

            if path in EXCLUDED_PATHS or path.startswith("/openapi"):
                return await call_next(request)

            if request.method == "OPTIONS":
                return await call_next(request)

            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

            token = auth_header.split("Bearer ")[-1]
            if not verify_token(token):
                raise HTTPException(status_code=401, detail="Invalid or expired token")

            return await call_next(request)

        except HTTPException as e:
            return Response(content=e.detail, status_code=e.status_code)


class LogRequestDataMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        raw_body = await request.body()
        logger_message = []

        logger_message.append(f"Поступил {request.method} запрос на {request.url.path}")
        logger_message.append(f"URL: {request.url}")

        headers = dict(request.headers)
        headers_json = json.dumps(headers, indent=4, ensure_ascii=False)
        logger_message.append(f"Заголовки запроса:\n{headers_json}")

        query_params = dict(request.query_params)
        query_params_json = json.dumps(query_params, indent=4, ensure_ascii=False)
        logger_message.append(f"Параметры запроса:\n{query_params_json}")

        content_type = request.headers.get("content-type", "")
        body = {}
        
        # Проверка, есть ли тело у запроса и не является ли это preflight (OPTIONS) запросом
        if request.method not in ("OPTIONS", "GET") and request.headers.get("content-length"):
            if content_type == "application/json":
                try:
                    body = await request.json()
                    body_json = json.dumps(body, indent=4, ensure_ascii=False)
                    logger_message.append(f"Тело запроса (JSON):\n{body_json}\n")
                except json.JSONDecodeError:
                    logger_message.append("Ошибка парсинга JSON-тела запроса")
            elif content_type == "application/x-www-form-urlencoded":
                form_data = await request.form()
                body = dict(form_data)
                form_data_json = json.dumps(body, indent=4, ensure_ascii=False)
                logger_message.append(f"Тело запроса (Form Data):\n{form_data_json}\n")
            else:
                logger_message.append(f"Тело запроса (неизвестный формат):\n{raw_body}\n")
        
        logger.debug("\n".join(logger_message))
        logger_message.clear()

        request.state.headers = headers
        request.state.query_params = query_params
        request.state.body = body

        request._body = raw_body  # Восстановление тела запроса для последующего использования
        response = await call_next(request)

        logger_message.append(f"Ответ на запрос {request.url.path}")
        logger_message.append(f"Статус ответа: {response.status_code}")
        response_headers = dict(response.headers)
        response_headers_json = json.dumps(response_headers, indent=4, ensure_ascii=False)
        logger_message.append(f"Заголовки ответа:\n{response_headers_json}")

        logger.debug("\n".join(logger_message))
        return response
