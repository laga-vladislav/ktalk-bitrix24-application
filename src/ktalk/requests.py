from httpx import AsyncClient

from src.models import BitrixAppStorageModel
from src.ktalk.models import MeetingModel, KTalkBackAnswerModel
from src.ktalk.utils import get_back_answer


async def create_meeting(meeting: MeetingModel, app_options: BitrixAppStorageModel) -> KTalkBackAnswerModel:
    async with AsyncClient() as client:
        meeting.start = meeting.start_ktalk
        meeting.end = meeting.end_ktalk
        print(meeting.model_dump())

        space_name = app_options.space
        email = app_options.admin_email
        api_key = app_options.api_key

        response = await client.post(
            url=f"https://{space_name}.ktalk.ru/api/emailCalendar/{email}",
            headers={"X-Auth-Token": api_key},
            json=meeting.model_dump()
        )
        return get_back_answer(response.json(), app_options)
