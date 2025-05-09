import uuid
import re
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel, Field, field_validator

from src.ktalk.validators import date_validator, timezone_validator, pincode_validator, bool_validator


class MeetingModel(BaseModel):
    subject: str
    description: str
    start: int | str = Field(
        description="Дата в формате timestamp, 'dd.mm.yyyy HH:MM:SS' или '%Y-%m-%dT%H:%M:%SZ'")
    end: int | str = Field(
        description="Дата в формате timestamp, 'dd.mm.yyyy HH:MM:SS' или '%Y-%m-%dT%H:%M:%SZ'")
    timezone: str = Field(description="Часовой пояс формата 'GMT+9'")
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
        # Конвертируем даты в UTC с учетом часового пояса
        self._start_robot, self._start_todo_activity, self._start_ktalk = self.convert_dates(self.start, self.timezone)
        self._end_robot, self._end_todo_activity, self._end_ktalk = self.convert_dates(self.end, self.timezone)

    @staticmethod
    def convert_dates(date_value, timezone_str):
        # Извлекаем смещение часового пояса
        match = re.match(r'GMT([+-]?\d+)', timezone_str.upper())
        if not match:
            raise ValueError("Invalid GMT format")
        offset_hours = int(match.group(1))
        offset = timedelta(hours=offset_hours)

        # Парсим дату
        if isinstance(date_value, int):
            dt = datetime.fromtimestamp(date_value / 1000, tz=timezone.utc)
        elif isinstance(date_value, str):
            try:
                dt = datetime.strptime(date_value, '%d.%m.%Y %H:%M:%S')
            except ValueError:
                try:
                    dt = datetime.strptime(date_value, '%Y-%m-%dT%H:%M:%SZ')
                except ValueError:
                    raise ValueError("Дата должна быть в формате timestamp, 'dd.mm.yyyy HH:MM:SS', или '%Y-%m-%dT%H:%M:%SZ'")
            dt = dt.replace(tzinfo=timezone.utc)  # Предполагаем, что строка в UTC
        else:
            raise ValueError("Дата должна быть числом или строкой в допустимом формате")

        # Конвертируем в UTC (дата в часовом поясе -> UTC)
        dt = dt - offset

        return (
            int(dt.timestamp() * 1000),  # timestamp в миллисекундах
            dt.strftime('%d.%m.%Y %H:%M:%S'),  # формат dd.mm.yyyy HH:MM:SS
            dt.strftime('%Y-%m-%dT%H:%M:%SZ')  # формат YYYY-MM-DDTHH:MM:SSZ
        )

    def _adjust_date(self, dt, is_utc, offset_hours):
        """Вспомогательный метод для корректировки даты по часовому поясу."""
        if not is_utc:
            dt = dt + timedelta(hours=offset_hours)
        return dt

    def start_robot(self, is_utc: bool = True) -> int:
        """Дата в формате timestamp. Если is_utc=False, возвращает в часовом поясе."""
        match = re.match(r'GMT([+-]?\d+)', self.timezone.upper())
        offset_hours = int(match.group(1)) if match else 0
        dt = datetime.fromtimestamp(self._start_robot / 1000, tz=timezone.utc)
        dt = self._adjust_date(dt, is_utc, offset_hours)
        return int(dt.timestamp() * 1000)

    def end_robot(self, is_utc: bool = True) -> int:
        """Дата в формате timestamp. Если is_utc=False, возвращает в часовом поясе."""
        match = re.match(r'GMT([+-]?\d+)', self.timezone.upper())
        offset_hours = int(match.group(1)) if match else 0
        dt = datetime.fromtimestamp(self._end_robot / 1000, tz=timezone.utc)
        dt = self._adjust_date(dt, is_utc, offset_hours)
        return int(dt.timestamp() * 1000)

    def start_todo_activity(self, is_utc: bool = True) -> str:
        """Дата в формате 'dd.mm.yyyy HH:MM:SS'. Если is_utc=False, возвращает в часовом поясе."""
        match = re.match(r'GMT([+-]?\d+)', self.timezone.upper())
        offset_hours = int(match.group(1)) if match else 0
        dt = datetime.fromtimestamp(self._start_robot / 1000, tz=timezone.utc)
        dt = self._adjust_date(dt, is_utc, offset_hours)
        return dt.strftime('%d.%m.%Y %H:%M:%S')

    def end_todo_activity(self, is_utc: bool = True) -> str:
        """Дата в формате 'dd.mm.yyyy HH:MM:SS'. Если is_utc=False, возвращает в часовом поясе."""
        match = re.match(r'GMT([+-]?\d+)', self.timezone.upper())
        offset_hours = int(match.group(1)) if match else 0
        dt = datetime.fromtimestamp(self._end_robot / 1000, tz=timezone.utc)
        dt = self._adjust_date(dt, is_utc, offset_hours)
        return dt.strftime('%d.%m.%Y %H:%M:%S')

    def start_ktalk(self, is_utc: bool = True) -> str:
        """Дата в формате '%Y-%m-%dT%H:%M:%SZ'. Если is_utc=False, возвращает в часовом поясе."""
        match = re.match(r'GMT([+-]?\d+)', self.timezone.upper())
        offset_hours = int(match.group(1)) if match else 0
        dt = datetime.fromtimestamp(self._start_robot / 1000, tz=timezone.utc)
        dt = self._adjust_date(dt, is_utc, offset_hours)
        return dt.strftime('%Y-%m-%dT%H:%M:%SZ')

    def end_ktalk(self, is_utc: bool = True) -> str:
        """Дата в формате '%Y-%m-%dT%H:%M:%SZ'. Если is_utc=False, возвращает в часовом поясе."""
        match = re.match(r'GMT([+-]?\d+)', self.timezone.upper())
        offset_hours = int(match.group(1)) if match else 0
        dt = datetime.fromtimestamp(self._end_robot / 1000, tz=timezone.utc)
        dt = self._adjust_date(dt, is_utc, offset_hours)
        return dt.strftime('%Y-%m-%dT%H:%M:%SZ')


class KTalkBackAnswerModel(BaseModel):
    """
    Использовать в связке с get_back_answer из ktalk.utils
    """
    url: str = ""
    sipSettings: dict = {}
    error: str = ""
