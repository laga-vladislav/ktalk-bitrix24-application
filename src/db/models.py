from pydantic import BaseModel


class PortalModel(BaseModel):
    member_id: str
    endpoint: str
    scope: str


class UserModel(BaseModel):
    user_id: int
    member_id: str
    id_auth: int
    is_admin: bool


class AuthModel(BaseModel):
    id_auth: int
    access_token: str
    refresh_token: str
    created_at: str
