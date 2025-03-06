import uuid
from datetime import datetime
from pydantic import BaseModel, Field, field_validator

from src.ktalk.validators import date_validator, timezone_validator, pincode_validator, bool_validator


class MeetingModel(BaseModel):
    # TODO: неверные названия для типов даты
    subject: str
    description: str
    start: str | int = Field(
        description="Дата в формате timestamp, 'dd.mm.yyyy HH:MM:SS' или '%Y-%m-%dT%H:%M:%S.%Z'")
    end: str | int = Field(
        description="Дата в формате timestamp, 'dd.mm.yyyy HH:MM:SS' или '%Y-%m-%dT%H:%M:%S.%Z'")
    start_robot: int = Field(
        default=None, description="Дата в формате timestamp", exclude=True)
    start_todo_activity: str = Field(
        default=None, description="Дата в формате 'dd.mm.yyyy HH:MM:SS'", exclude=True)
    start_ktalk: str = Field(
        default=None, description="Дата в формате '%Y-%m-%dT%H:%M:%S.%Z'", exclude=True)
    end_robot: int = Field(
        default=None, description="Дата в формате timestamp", exclude=True)
    end_todo_activity: str = Field(
        default=None, description="Дата в формате 'dd.mm.yyyy HH:MM:SS'", exclude=True)
    end_ktalk: str = Field(
        default=None, description="Дата в формате '%Y-%m-%dT%H:%M:%S.%Z'", exclude=True)
    timezone: str = Field(description="Часовой пояс формата 'GMT+9'")
    roomName: str = Field(default_factory=lambda: str(uuid.uuid4()))
    allowAnonymous: bool | str = Field(
        default=True, description="Доступ внешних пользователей. Может быть bool, либо строкой и принимать значения 'Y' или 'N'")
    enableSip: bool | str = Field(
        description="Может быть bool, либо строкой и принимать значения 'Y' или 'N'")
    enableAutoRecording: bool | str = Field(
        description="Может быть bool, либо строкой и принимать значения 'Y' или 'N'")
    pinCode: str | int = ""

    @field_validator('start', 'end')
    def validate_date(cls, date_value):
        date_value = date_validator(date_value)
        return date_value

    @field_validator('timezone')
    def validate_timezone(cls, timezone_value):
        timezone_value = timezone_validator(timezone_value)
        return timezone_value

    @field_validator('pinCode')
    def validate_pin_code(cls, pinCode_value):
        pinCode_value = pincode_validator(pinCode_value)
        return pinCode_value

    @field_validator('allowAnonymous', 'enableSip', 'enableAutoRecording')
    def validate_bool(cls, value):
        value = bool_validator(value)
        return value

    def model_post_init(self, __context__):
        # Обработка дат после инициализации
        self.start_todo_activity, self.start_robot, self.start_ktalk = self.convert_dates(
            self.start)
        self.end_todo_activity, self.end_robot, self.end_ktalk = self.convert_dates(
            self.end)

    @staticmethod
    def convert_dates(date_value):
        """Конвертирует дату в формате timestamp, 'dd.mm.yyyy HH:MM:SS' и 'YYYY-MM-DDTHH:MM:SSZ'"""
        if isinstance(date_value, int):
            # Преобразование миллисекунд в секунды
            dt = datetime.fromtimestamp(date_value // 1000)
        elif isinstance(date_value, str):
            # Проверяем формат 'dd.mm.yyyy HH:MM:SS'
            try:
                dt = datetime.strptime(date_value, '%d.%m.%Y %H:%M:%S')
            except ValueError:
                # Проверяем формат 'YYYY-MM-DDTHH:MM:SSZ'
                try:
                    dt = datetime.strptime(date_value, '%Y-%m-%dT%H:%M:%SZ')
                except ValueError:
                    raise ValueError(
                        "Дата должна быть в формате timestamp, 'dd.mm.yyyy HH:MM:SS', либо '%Y-%m-%dT%H:%M:%SZ'"
                    )
        else:
            raise ValueError(
                "Дата должна быть в формате timestamp, 'dd.mm.yyyy HH:MM:SS' или '%Y-%m-%dT%H:%M:%SZ'")

        return int(dt.timestamp() * 1000), dt.strftime('%d.%m.%Y %H:%M:%S'), dt.strftime('%Y-%m-%dT%H:%M:%SZ')


class KTalkBackAnswerModel(BaseModel):
    """
    Использовать в связке с get_back_answer из ktalk.utils
    """
    url: str = ""
    sipSettings: dict = {}
    error: str = ""
