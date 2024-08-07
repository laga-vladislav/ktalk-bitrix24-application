import json
from typing import Any, Dict, Optional
from pydantic import BaseModel

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

app = FastAPI()


class RequestData(BaseModel):
    method: str
    url: str
    headers: Optional[Dict[str, Any]]
    query_params: Optional[Dict[str, str]]
    body: Optional[Dict[str, Any]]


@app.middleware("http")
async def log_request_data(request: Request, call_next):
    # Выводим метод запроса и URL
    print(f"Метод запроса: {request.method}")
    print(f"URL: {request.url}\n")

    # Выводим заголовки в формате JSON
    headers = dict(request.headers)
    headers_json = json.dumps(headers, indent=4, ensure_ascii=False)
    print(f"Заголовки запроса:\n{headers_json}\n")

    # Выводим параметры запроса
    query_params = dict(request.query_params)
    query_params_json = json.dumps(query_params, indent=4, ensure_ascii=False)
    print(f"Параметры запроса:\n{query_params_json}\n")

    # Выводим тип содержимого тела запроса
    content_type = request.headers.get("content-type")

    # Если тело запроса в формате JSON, выводим его
    if content_type == "application/json":
        body = await request.json()
        body_json = json.dumps(body, indent=4, ensure_ascii=False)
        print(f"Тело запроса (JSON):\n{body_json}\n")

    # Если тело запроса в формате x-www-form-urlencoded, выводим его
    elif content_type == "application/x-www-form-urlencoded":
        # Получение данных формы
        form_data = await request.form()

        # Преобразование данных формы в словарь
        body = dict(form_data)

        # Проверка и преобразование строки JSON в словарь
        if "PLACEMENT_OPTIONS" in body:
            try:
                # Преобразование строки JSON в словарь
                body["PLACEMENT_OPTIONS"] = json.loads(body["PLACEMENT_OPTIONS"])
            except json.JSONDecodeError:
                # Если JSON некорректный, оставить как есть
                body["PLACEMENT_OPTIONS"] = body["PLACEMENT_OPTIONS"]
        form_body_json = json.dumps(body, indent=4, ensure_ascii=False)
        print(f"Тело запроса (Form Data):\n{form_body_json}\n")


    request.state.data = RequestData(
        method=request.method,
        url=str(request.url),
        headers=headers,
        query_params=query_params,
        body=body,
    )

    # Обрабатываем запрос
    response = await call_next(request)

    # Выводим статус ответа и заголовки
    print(f"Статус ответа: {response.status_code}")
    response_headers = dict(response.headers)
    response_headers_json = json.dumps(response_headers, indent=4, ensure_ascii=False)
    print(f"Заголовки ответа:\n{response_headers_json}")

    return response


@app.post("/install")
async def install(request: Request):
    # Установка приложения

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
    # Работа приложения

    return request.state.data.body


if __name__ == "__main__":
    uvicorn.run(
        app="check_requests_fastapi:app", host="127.0.0.1", port=8000, reload=True
    )
