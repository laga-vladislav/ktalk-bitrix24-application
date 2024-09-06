from crest.models import AuthTokens, CallRequest
from src.models import PortalModel
from src.ktalk.models import MeetingModel
from crest.crest import CRestBitrix24
from src.ktalk.models import MeetingModel, ParticipantsModel


async def add_todo_activity(
    crest: CRestBitrix24,
    portal: PortalModel,
    creator_id: int,
    owner_id: int,
    meeting: MeetingModel,
    meeting_url: str,
    participants: ParticipantsModel,
    owner_type_id: int = 2
):
    """
    Создать дело внутри объекта CRM.
    owner_id - id объекта CRM. Например, id сделки.
    owner_type_id - тип объекта CRM. Например, 2 - это сделка.
    """
    selected_clients_dicts = [client.model_dump()
                              for client in participants.selectedClients]
    # meeting_str_date = MeetingKTalkFormatDateModel(**dict(meeting))
    print(meeting)
    call_request = CallRequest(
        method="crm.activity.todo.add",
        params={
            'ownerTypeId': owner_type_id,
            'ownerId': owner_id,
            'title': meeting.subject,
            'description': meeting.description,
            'deadline': meeting.end,
            'responsibleId': creator_id,
            'settings': [
                {
                    'link': meeting_url,
                    'id': 'link'
                },
                {
                    'from': meeting.start,
                    'to': meeting.end,
                    'duration': 1200000,
                    'location': '',
                    'selectedUserIds': participants.colleguesId,
                    'id': 'calendar'
                },
                {
                    'selectedClients': selected_clients_dicts,
                    'id': 'client'
                }
            ],
            "colorId": 5,
            "pingOffsets": [0, 15, 60, 1440]
        }
    )
    endpoint = portal.client_endpoint
    tokens = AuthTokens(
        access_token=portal.access_token,
        refresh_token=portal.refresh_token
    )
    response = await crest.call(
        request=call_request,
        client_endpoint=endpoint,
        auth_tokens=tokens
    )
    return response
