from pydantic import BaseModel, Field
import uuid


class BitrixKTalkStorageModel(BaseModel):
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
    roomName: str = Field(default=str(uuid.uuid4()))
    allowAnonymous: bool
    enableSip: bool
    pinCode: str
    # pinCode: int = Field(ge=1000, lt=1000000)
    enableAutoRecording: bool
    isRecurring: bool


class ParticipantsModel(BaseModel):
    colleguesId: list[int]
    selectedClients: list[dict]


class KTalkBackAnswer(BaseModel):
    url: str
    sipSettings: dict
    error: str | None = None
