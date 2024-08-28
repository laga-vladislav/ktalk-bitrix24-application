from datetime import datetime, timezone
from pydantic import BaseModel, Field, model_validator
import uuid


class BitrixAppStorageModel(BaseModel):
    space: str
    api_key: str
    admin_email: str
    member_id: str


class MeetingModel(BaseModel):
    subject: str
    description: str
    start: int = Field(description="Дата в формате timestamp")
    end: int = Field(description="Дата в формате timestamp")
    timezone: str
    roomName: str = Field(default_factory=lambda: str(uuid.uuid4()))
    allowAnonymous: bool
    enableSip: bool
    pinCode: str  = ""
    # pinCode: int = Field(ge=1000, lt=1000000)
    enableAutoRecording: bool
    isRecurring: bool


class MeetingStringDateModel(MeetingModel):
    """
    Нужен для удобного преобразования даты одного вида в другую.
    Чтобы не пришлось руками менять дату при отправке запроса КТолк.
    """
    start: str = Field(description="Дата формата 2024-08-28T04:00:00.000Z")
    end: str = Field(description="Дата формата 2024-08-28T04:00:00.000Z")

    @staticmethod
    def convert_timestamp_to_string(timestamp: int) -> str:
        return datetime.fromtimestamp(timestamp / 1000, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    @model_validator(mode='before')
    def convert_timestamps(cls, values):
        if isinstance(values.get('start'), int):
            values['start'] = cls.convert_timestamp_to_string(values['start'])
        if isinstance(values.get('end'), int):
            values['end'] = cls.convert_timestamp_to_string(values['end'])
        return values


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
    url: str = ""
    sipSettings: dict = {}
    error: str = ""
