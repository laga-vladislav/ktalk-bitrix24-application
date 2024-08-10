from fastapi import Depends, FastAPI, Query, Request
from fastapi.responses import HTMLResponse

from crest.crest import CRestBitrix24
from crest.models import CallRequest
from src.middleware.middleware import LogRequestDataMiddleware
from src.middleware.lifespan import lifespan
# from src.logger.custom_logger import logger


app = FastAPI(lifespan=lifespan)

app.add_middleware(LogRequestDataMiddleware)


def get_crest():
    return app.state.CRest

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

@app.get("/auth_callback")
async def aouth_get_code(request: Request, CRest: CRestBitrix24 = Depends(get_crest), code: str = Query(None)):
    # можно брать code из middleware
    # code = request.state.query_params.get('code')
    result = await CRest.get_token(code=code)
    return result