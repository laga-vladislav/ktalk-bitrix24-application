from fastapi import FastAPI

from src.middleware.lifespan import lifespan  # noqa: E402
from src.middleware.middleware import LogRequestDataMiddleware  # noqa: E402, F401
from src.router import handler, install, placement, create_meeting, ktalk_robot  # noqa: E402


app = FastAPI(lifespan=lifespan)

app.add_middleware(LogRequestDataMiddleware)

app.include_router(handler.router)
app.include_router(install.router)
app.include_router(placement.router)
app.include_router(create_meeting.router)
app.include_router(ktalk_robot.router)
