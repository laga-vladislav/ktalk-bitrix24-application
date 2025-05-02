from httpx import AsyncClient

from src.models import KtalkSpaceModel
from src.ktalk.models import MeetingModel, KTalkBackAnswerModel
from src.ktalk.utils import get_back_answer


async def create_meeting(meeting: MeetingModel, ktalk_space: KtalkSpaceModel) -> KTalkBackAnswerModel:
    async with AsyncClient() as client:
        meeting.start = meeting.start_ktalk
        meeting.end = meeting.end_ktalk
        print(meeting.model_dump())

        space_name = ktalk_space.space
        email = ktalk_space.admin_email
        api_key = ktalk_space.api_key

        response = await client.post(
            url=f"https://{space_name}.ktalk.ru/api/emailCalendar/{email}",
            headers={"X-Auth-Token": api_key},
            json=meeting.model_dump()
        )
        return get_back_answer(response.json(), ktalk_space)
