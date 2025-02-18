from datetime import datetime, timezone
from pydantic import BaseModel


class PortalModel(BaseModel):
    """
    Администратор портала
    """
    member_id: str
    client_endpoint: str
    scope: str
    access_token: str
    refresh_token: str
    updated_at: datetime | None = None


class UserModel(BaseModel):
    """
    Пользователь портала, в том числе администраторы
    """
    id: int
    member_id: str
    name: str
    last_name: str
    is_admin: bool
    access_token: str
    refresh_token: str
    updated_at: datetime | None = datetime.now(timezone.utc)
