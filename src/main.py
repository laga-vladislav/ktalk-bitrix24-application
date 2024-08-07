from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

from src.middleware.middleware import LogRequestDataMiddleware
from src.middleware.lifespan import lifespan
# from src.logger.custom_logger import logger


app = FastAPI(lifespan=lifespan)

app.add_middleware(LogRequestDataMiddleware)


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
