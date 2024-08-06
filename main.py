from urllib.parse import parse_qs
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel
import uvicorn

from crest import CRest

from environs import Env

# Инициализация Env
env = Env()
env.read_env(override=True)

app = FastAPI()


@app.post("/profile")
async def show_profile_info():
    result = CRest.call(
        method="profile",
    )
    return result


@app.post("/add_test_contact")
async def add_contact():
    class Contact(BaseModel):
        name: str
        last_name: str
        email: str
        phone: str

    contact = Contact(
        name="test-name",
        last_name="test-last-name",
        email="test@gmail.com",
        phone="123456",
    )
    result = CRest.call(
        method="crm.contact.add",
        params={
            "FIELDS": {
                "NAME": contact.name,
                "LAST_NAME": contact.last_name,
                "EMAIL": [{"VALUE": contact.email, "VALUE_TYPE": "WORK"}],
                "PHONE": [{"VALUE": contact.phone, "VALUE_TYPE": "WORK"}],
            }
        },
    )
    return result


@app.post("/placement")
async def placement():
    result = CRest.call(
        method="user.current",
    )
    return result


@app.post("/install", response_class=HTMLResponse)
async def install(request: Request):
    # Встройка виджета в интерфейс
    CRest.call(
        method="placement.bind",
        params={
            "PLACEMENT": "CRM_CONTACT_DETAIL_ACTIVITY",
            "HANDLER": env.str("SERVER_URL") + "/placement",
            "TITLE": "myapp",
        },
    )

    # Извлечение параметров из URL
    query_params = dict(request.query_params)

    # Чтение и декодирование тела запроса
    body = await request.body()
    body_params = parse_qs(body.decode("utf-8"))

    # Преобразование значений из списка в одиночные значения
    body_params = {k: v[0] for k, v in body_params.items()}

    # Объединение параметров из строки запроса и тела запроса
    combined_data = {**query_params, **body_params}

    print(combined_data)

    result = CRest.install_app(combined_data)

    if result["rest_only"]:
        return

    # Определяем сообщение об установке в зависимости от результата
    installation_message = (
        "Установка завершена" if result["install"] else "Ошибка установки"
    )

    # Генерируем HTML-контент в зависимости от результата установки
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <title>Установка приложения</title>
        <script src="//api.bitrix24.com/api/v1/"></script>
        <script>
            BX24.init(function(){{
                BX24.installFinish();
            }});
        </script>
    </head>
    <body>
        <p>{installation_message}</p>
    </body>
    </html>
    """

    # Возвращаем сгенерированный HTML
    return html_content


@app.get("/check_server")
async def check_server():
    return CRest.check_server()


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("favicon.ico")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app="main:app", host="127.0.0.1", port=8000, reload=True)
