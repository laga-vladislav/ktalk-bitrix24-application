from datetime import datetime
from pydantic import BaseModel, Field


class BitrixCalendarModel(BaseModel):
    id: int = Field(..., alias="ID")
    name: str = Field(..., alias="NAME")
    description: str = Field(..., alias="DESCRIPTION")
    # link: str = Field(..., validation_alias=AliasPath('EXPORT', 'LINK'))
    # ссылка оказалась ссылкой на экспорт, кто бы мог подумать. Вырезал


class SelectedClientsModel(BaseModel):
    entityId: int
    entityTypeId: int
    isAvailable: bool = Field(default=True)


class ParticipantsModel(BaseModel):
    colleguesId: list[int]
    selectedClients: list[SelectedClientsModel]


class PortalModel(BaseModel):
    """
    Портал Bitrix24, подключённый к системе
    """
    member_id: str
    client_endpoint: str
    scope: str


class KtalkSpaceModel(BaseModel):
    """
    Интеграция портала с Ktalk
    """
    member_id: str
    space: str
    api_key: str
    admin_email: str


class UserModel(BaseModel):
    """
    Пользователь портала
    """
    user_id: int
    member_id: str
    name: str
    last_name: str
    is_admin: bool


class UserAuthModel(BaseModel):
    """
    Данные  пользователя
    """
    user_id: int
    member_id: str
    client_endpoint: str = Field(exclude=True)  # exclude необходим при преобразовании из модели в схему. У схемы нет такого поля.
    access_token: str
    refresh_token: str
    updated_at: datetime = Field(default=datetime.now())

    def dict_with_excluded_fields(self):
        return {**self.model_dump(mode="json"), "client_endpoint": self.client_endpoint}
    