from fastapi import APIRouter, HTTPException, Request
from src.auth import verify_token

router = APIRouter()


@router.post("/get-jwt-payload")
async def verify(request: Request):
    auth_header = request.headers.get("Authorization")
    token = auth_header.split("Bearer ")[-1]
    payload = verify_token(token=token)
    if payload:
        return payload
    raise HTTPException(status_code=401, detail="Invalid or expired token")
