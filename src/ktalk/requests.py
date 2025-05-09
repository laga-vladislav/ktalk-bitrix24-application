from httpx import AsyncClient

from src.models import KtalkSpaceModel
from src.ktalk.models import MeetingModel, KTalkBackAnswerModel
from src.ktalk.utils import get_back_answer

from src.logger.custom_logger import logger


async def create_meeting(meeting: MeetingModel, ktalk_space: KtalkSpaceModel) -> KTalkBackAnswerModel:
    async with AsyncClient() as client:
        meeting_temp = meeting.model_copy()
        meeting_temp.start = str(meeting_temp.start_ktalk())
        meeting_temp.end = str(meeting_temp.end_ktalk())
        logger.debug(meeting_temp)

        space_name = ktalk_space.space
        email = ktalk_space.admin_email
        api_key = ktalk_space.api_key

        response = await client.post(
            url=f"https://{space_name}.ktalk.ru/api/emailCalendar/{email}",
            headers={"X-Auth-Token": api_key},
            json=meeting_temp.model_dump()
        )
        logger.debug(response)
        if response.status_code == 403:
            logger.error(response)
            return KTalkBackAnswerModel(error="Неверный API ключ, либо тариф КТолк пространства")
        if response.status_code != 200:
            logger.error(response.json())
            return KTalkBackAnswerModel(error=f"Произошла ошибка при создании встречи: {response.json()['errorMessage']}")
        return get_back_answer(response.json(), ktalk_space)
