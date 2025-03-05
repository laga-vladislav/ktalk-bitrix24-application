from fastapi import APIRouter, Response, HTTPException
from pydantic import BaseModel
from src.auth import verify_token

router = APIRouter()


class TokenRequest(BaseModel):
    jwt: str


@router.post("/verify-jwt")
async def verify(jwt: TokenRequest):
    token = verify_token(jwt.jwt)
    if token:
        return token
    raise HTTPException(status_code=401, detail="Invalid or expired token")
