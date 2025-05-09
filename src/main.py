import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.middleware.lifespan import lifespan  # noqa: E402
from src.middleware.middleware import LogRequestDataMiddleware, JWTAuthMiddleware  # noqa: E402, F401
from src.router import handler, install, placement, create_external_meeting, create_internal_meeting, get_payload, set_settings  # noqa: E402


app = FastAPI(lifespan=lifespan)

app.add_middleware(LogRequestDataMiddleware)
app.add_middleware(JWTAuthMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://" + os.getenv("FRONT_DOMAIN"),
        "http://localhost:3000",
        "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(handler.router)
app.include_router(install.router)
app.include_router(placement.router)
app.include_router(create_external_meeting.router)
app.include_router(create_internal_meeting.router)
app.include_router(get_payload.router)
app.include_router(set_settings.router)
