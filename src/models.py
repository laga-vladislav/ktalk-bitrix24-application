from datetime import datetime, timezone
from pydantic import BaseModel, Field, AliasPath


class BitrixCalendarModel(BaseModel):
    id: int = Field(..., alias="ID")
    name: str = Field(..., alias="NAME")
    description: str = Field(..., alias="DESCRIPTION")
    link: str = Field(..., validation_alias=AliasPath('EXPORT', 'LINK'))


class BitrixAppStorageModel(BaseModel):
    space: str
    api_key: str
    admin_email: str
    member_id: str


class SelectedClientsModel(BaseModel):
    entityId: int
    entityTypeId: int
    isAvailable: bool = Field(default=True)


class ParticipantsModel(BaseModel):
    colleguesId: list[int]
    selectedClients: list[SelectedClientsModel]


class AppOptionModel(BaseModel):
    option_name: str
    option_data: str


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
