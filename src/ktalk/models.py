from pydantic import BaseModel, Field
import uuid


class BitrixAppStorageModel(BaseModel):
    space: str
    api_key: str
    admin_email: str
    member_id: str


class MeetingModel(BaseModel):
    subject: str
    description: str
    start: str = Field(description="Формат типа 2024-08-28T03:00:00.000Z")
    end: str = Field(description="Формат типа 2024-08-28T04:00:00.000Z")
    timezone: str
    roomName: str = Field(default_factory=lambda: str(uuid.uuid4()))
    allowAnonymous: bool
    enableSip: bool
    pinCode: str
    # pinCode: int = Field(ge=1000, lt=1000000)
    enableAutoRecording: bool
    isRecurring: bool


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


class KTalkBackAnswerModel(BaseModel):
    url: str
    sipSettings: dict
    error: str | None = None
