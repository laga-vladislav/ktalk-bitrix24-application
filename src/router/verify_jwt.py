from fastapi import APIRouter, Response

router = APIRouter()


@router.post("/verify-jwt")
async def verify():
    return Response(status_code=200)
