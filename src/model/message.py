from datetime import datetime
from dataclasses import dataclass
from pydantic import BaseModel
from typing import *

@dataclass()
class FrontendUser:
    id: int
    username: str


@dataclass()
class AbstractMessage:
    text: str
    date: datetime
    from_user: FrontendUser


@dataclass()
class RestApiMessage(AbstractMessage):
    pass


class AddMessageQueuePayload(BaseModel):
    text: str
    date: datetime
    from_user: FrontendUser


class RetrieveMessageQueuePayload(BaseModel):
    # id
    user_id: int
    # all_sliders with int values
    # {
    #   "anger_level": 0,
    #    ...
    # }
    sliders: Dict[str, int]

class TowardsFrontendPayload(BaseModel):
    text: str
    function: str
    args: List[str]