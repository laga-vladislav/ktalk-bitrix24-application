from datetime import datetime
from pydantic import BaseModel


class PortalModel(BaseModel):
    member_id: str
    endpoint: str
    scope: str
    access_token: str
    refresh_token: str
    updated_at: datetime | None = None
