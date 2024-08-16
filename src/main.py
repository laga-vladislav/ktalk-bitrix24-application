from fastapi import FastAPI

from src.middleware.lifespan import lifespan  # noqa: E402
from src.middleware.middleware import LogRequestDataMiddleware  # noqa: E402, F401
from src.router import handler, install, placement  # noqa: E402


app = FastAPI(lifespan=lifespan)

app.add_middleware(LogRequestDataMiddleware)

app.include_router(handler.router)
app.include_router(install.router)
app.include_router(placement.router)
