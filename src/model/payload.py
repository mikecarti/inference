from datetime import datetime
from typing import Dict, List

from pydantic import BaseModel

from src.model.message import FrontendUser, UserMessage


class AddMessageQueuePayload(BaseModel):
    """
    Payload for queue message processing on Helpdesk
    """
    text: str
    date: datetime
    from_user: FrontendUser

    def to_user_message(self) -> UserMessage:
        return UserMessage(
            text=self.text,
            date=self.date,
            from_user=FrontendUser(
                id=self.from_user.id,
                username=self.from_user.username
            )
        )


class RetrieveMessageQueuePayload(BaseModel):
    """
    Payload for retrieving processed messages on Helpdesk
    """
    # Usually id is IP and Port
    user_id: str
    # all_sliders with int values
    # {
    #   "anger_level": 0,
    #    ...
    # }
    sliders: Dict[str, int]


class TowardsFrontendPayload(BaseModel):
    """
    Payload for sending response on Frontend
    """
    text: str
    function: str
    args: List[str]
