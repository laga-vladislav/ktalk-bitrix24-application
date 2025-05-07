import uuid
from datetime import datetime
from pydantic import BaseModel, Field, field_validator

from src.ktalk.validators import date_validator, timezone_validator, pincode_validator, bool_validator


class MeetingModel(BaseModel):
    # Короче, узнал инфу про дату в КТолке:
    # дату надо посылать в в UTC0, отправляя часовой пояс.
    # Он там сам уже прибавляет в зависимости от пояса. Бред, ес честно.
    subject: str
    description: str
    start: int | str = Field(
        description="Дата в формате timestamp, 'dd.mm.yyyy HH:MM:SS' или '%Y-%m-%dT%H:%M:%S.%Z'")
    end: int | str = Field(
        description="Дата в формате timestamp, 'dd.mm.yyyy HH:MM:SS' или '%Y-%m-%dT%H:%M:%S.%Z'")
    timezone: str = Field(description="Часовой пояс формата 'GMT+9'")
    roomName: str = Field(default_factory=lambda: str(uuid.uuid4()))
    allowAnonymous: bool | str = Field(
        default=True, description="Доступ внешних пользователей: bool или 'Y'/'N'")
    enableSip: bool | str = Field(
        description="Включить SIP: bool или 'Y'/'N'")
    enableAutoRecording: bool | str = Field(
        description="Включить автозапись: bool или 'Y'/'N'")
    pinCode: str | int = ""

    _start_robot: int | None = None
    _start_todo_activity: str | None = None
    _start_ktalk: str | None = None
    _end_robot: int | None = None
    _end_todo_activity: str | None = None
    _end_ktalk: str | None = None

    @field_validator('start', 'end')
    @classmethod
    def validate_date(cls, value):
        return date_validator(value)

    @field_validator('timezone')
    @classmethod
    def validate_timezone(cls, value):
        return timezone_validator(value)

    @field_validator('pinCode')
    @classmethod
    def validate_pin_code(cls, value):
        return pincode_validator(value)

    @field_validator('allowAnonymous', 'enableSip', 'enableAutoRecording')
    @classmethod
    def validate_bool(cls, value):
        return bool_validator(value)

    def model_post_init(self, __context__):
        self._start_robot, self._start_todo_activity, self._start_ktalk = self.convert_dates(self.start)
        self._end_robot, self._end_todo_activity, self._end_ktalk = self.convert_dates(self.end)

    @staticmethod
    def convert_dates(date_value):
        if isinstance(date_value, int):
            dt = datetime.fromtimestamp(date_value / 1000)
        elif isinstance(date_value, str):
            try:
                dt = datetime.strptime(date_value, '%d.%m.%Y %H:%M:%S')
            except ValueError:
                try:
                    dt = datetime.strptime(date_value, '%Y-%m-%dT%H:%M:%SZ')
                except ValueError:
                    raise ValueError("Дата должна быть в формате timestamp, 'dd.mm.yyyy HH:MM:SS', или '%Y-%m-%dT%H:%M:%SZ'")
        else:
            raise ValueError("Дата должна быть числом или строкой в допустимом формате")

        return int(dt.timestamp() * 1000), dt.strftime('%d.%m.%Y %H:%M:%S'), dt.strftime('%Y-%m-%dT%H:%M:%SZ')

    @property
    def start_robot(self) -> int:
        """
        Дата в формате timestamp
        """
        return self._start_robot

    @property
    def end_robot(self) -> int:
        """
        Дата в формате timestamp
        """
        return self._end_robot

    @property
    def start_todo_activity(self) -> str:
        """
        Дата в формате 'dd.mm.yyyy HH:MM:SS
        """
        return self._start_todo_activity

    @property
    def end_todo_activity(self) -> str:
        """
        Дата в формате 'dd.mm.yyyy HH:MM:SS
        """
        return self._end_todo_activity

    @property
    def start_ktalk(self) -> str:
        """
        Дата в формате '%Y-%m-%dT%H:%M:%S.%Z
        """
        return self._start_ktalk

    @property
    def end_ktalk(self) -> str:
        """
        Дата в формате '%Y-%m-%dT%H:%M:%S.%Z
        """
        return self._end_ktalk


class KTalkBackAnswerModel(BaseModel):
    """
    Использовать в связке с get_back_answer из ktalk.utils
    """
    url: str = ""
    sipSettings: dict = {}
    error: str = ""
