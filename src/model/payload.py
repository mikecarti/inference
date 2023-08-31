from datetime import datetime
from typing import Dict, List

from pydantic import BaseModel

from src.model.message import FrontendUser


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
