import json

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

from logger.custom_logger import logger
from utils.parser import parse_form_data

app = FastAPI()


@app.middleware("http")
async def log_request_data(request: Request, call_next):
    logger_message = []

    # Выводим метод запроса и URL
    logger_message.append(f"Поступил {request.method} запрос на {request.url.path}")
    logger_message.append(f"URL: {request.url}")

    # Выводим заголовки в формате JSON
    headers = dict(request.headers)

    headers_json = json.dumps(headers, indent=4, ensure_ascii=False)
    logger_message.append(f"Заголовки запроса:\n{headers_json}")

    # Выводим параметры запроса
    query_params = dict(request.query_params)

    query_params_json = json.dumps(query_params, indent=4, ensure_ascii=False)
    logger_message.append(f"Параметры запроса:\n{query_params_json}")

    # Тип содержимого тела запроса
    content_type = request.headers.get("content-type")
    body = {}

    # Если тело запроса в формате JSON
    if content_type == "application/json":
        body = await request.json()

        body_json = json.dumps(body, indent=4, ensure_ascii=False)
        logger_message.append(f"Тело запроса (JSON):\n{body_json}")

    # Если тело запроса в формате Form Data
    elif content_type == "application/x-www-form-urlencoded":
        body = await request.form()
        body = dict(body)
        body = parse_form_data(body)

        form_data_json = json.dumps(body, indent=4, ensure_ascii=False)
        logger_message.append(f"Тело запроса (Form Data):\n{form_data_json}")

    # Логирование информации о запросе
    logger.debug("\n".join(logger_message))
    logger_message = []

    # Сохранение информации о запросе
    request.state.headers = headers
    request.state.query_params = query_params
    request.state.body = body

    # Передача запроса обработчику
    response = await call_next(request)

    # Логирование информации об ответе
    logger_message.append(f"Ответ на запрос {request.url.path}")
    logger_message.append(f"Статус ответа: {response.status_code}")
    response_headers = dict(response.headers)
    response_headers_json = json.dumps(response_headers, indent=4, ensure_ascii=False)
    logger_message.append(f"Заголовки ответа:\n{response_headers_json}")

    # Логирование информации о запросе
    logger.debug("\n".join(logger_message))
    logger_message = []

    return response


@app.post("/install")
async def install(request: Request):
    html_content = """
        <!DOCTYPE html>
        <html lang="ru">
        <head>
            <title>Installation</title>
            <script src="//api.bitrix24.com/api/v1/"></script>
            <script>
                BX24.init(function(){
                    BX24.installFinish();
                });
            </script>
        </head>
        <body>
            <p>Installation finished</p>
        </body>
        </html>
    """
    return HTMLResponse(content=html_content, status_code=200)


@app.post("/handler")
async def handler(request: Request):
    return request.state.body


if __name__ == "__main__":
    uvicorn.run(
        app="check_requests_fastapi:app", host="127.0.0.1", port=8000, reload=True
    )
