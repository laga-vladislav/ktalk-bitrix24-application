from datetime import datetime, timezone
from pydantic import BaseModel, Field, model_validator, field_validator
import uuid


class BitrixAppStorageModel(BaseModel):
    space: str
    api_key: str
    admin_email: str
    member_id: str


class MeetingModel(BaseModel):
    subject: str
    description: str
    start: str | int = Field(
        description="Дата в формате timestamp или 'dd.mm.yyyy HH:MM:SS'")
    end: str | int = Field(
        description="Дата в формате timestamp или 'dd.mm.yyyy HH:MM:SS'")
    timezone: str = Field(description="Часовой пояс формата 'GMT+9'")
    roomName: str = Field(default_factory=lambda: str(uuid.uuid4()))
    allowAnonymous: bool | str = Field(
        default=True, description="Доступ внешних пользователей. Может быть bool, либо строкой и принимать значения 'Y' или 'N'")
    enableSip: bool | str = Field(
        description="Может быть bool, либо строкой и принимать значения 'Y' или 'N'")
    enableAutoRecording: bool | str = Field(
        description="Может быть bool, либо строкой и принимать значения 'Y' или 'N'")
    pinCode: str | int = ""

    @field_validator('timezone')
    def validate_timezone(cls, timezone_value):
        timezone_value = timezone_value.upper()
        if 'GMT' not in timezone_value:
            raise ValueError("Часовой пояс должен начинаться с 'GMT'")
        elif '+' not in timezone_value and '-' not in timezone_value:
            raise ValueError("Часовой пояс должен содержать '+' или '-'")
        elif timezone_value.count('+') > 1 or timezone_value.count('-') > 1:
            raise ValueError(
                "Часовой пояс должен содержать только один знак '+' или '-'")
        else:
            try:
                int(timezone_value.split('+')
                    [1]) if '+' in timezone_value else int(timezone_value.split('-')[1])
            except ValueError:
                raise ValueError("Часовой пояс должен содержать цифры")
        return timezone_value

    @field_validator('pinCode')
    def validate_pin_code(cls, pinCode_value):
        if isinstance(pinCode_value, int):
            pinCode_value = str(pinCode_value)
        else:
            try:
                int(pinCode_value)
            except ValueError:
                raise ValueError("Пин код должен содержать только цифры")

        if any((len(pinCode_value) < 4, len(pinCode_value) > 6)):
            raise ValueError("Пин код должен содержать от 4 до 6 цифр")
        return pinCode_value

    @field_validator('allowAnonymous', 'enableSip', 'enableAutoRecording')
    def validate_bool(cls, value):
        if isinstance(value, str):
            value = value.upper()

            if value not in ['Y', 'N']:
                raise ValueError(
                    "Значение должно быть 'Y' или 'N', либо булевым значением")

            return True if value == 'Y' else False
        return value


class MeetingKTalkFormatDateModel(MeetingModel):
    """
    Модель для преобразования дат в формат '%Y-%m-%dT%H:%M:%S.%fZ'
    """

    @staticmethod
    def convert_timestamp_to_string(timestamp: int) -> str:
        return datetime.fromtimestamp(timestamp / 1000, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    @staticmethod
    def convert_custom_format_to_string(date_str: str) -> str:
        dt = datetime.strptime(date_str, "%d.%m.%Y %H:%M:%S")
        return dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    @model_validator(mode='before')
    def convert_dates(cls, values):
        start = values.get('start')
        end = values.get('end')

        if isinstance(start, int):
            values['start'] = cls.convert_timestamp_to_string(start)
        elif isinstance(start, str):
            try:
                values['start'] = cls.convert_custom_format_to_string(start)
            except ValueError:
                pass  # Если формат уже правильный, оставляем как есть

        if isinstance(end, int):
            values['end'] = cls.convert_timestamp_to_string(end)
        elif isinstance(end, str):
            try:
                values['end'] = cls.convert_custom_format_to_string(end)
            except ValueError:
                pass  # Если формат уже правильный, оставляем как есть

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
    """
    Использовать в связке с get_back_answer из ktalk.utils
    """
    url: str = ""
    sipSettings: dict = {}
    error: str = ""
