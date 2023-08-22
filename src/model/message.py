from datetime import datetime
from dataclasses import dataclass
from pydantic import BaseModel


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


class MessagePayload(BaseModel):
    text: str
    date: datetime
    from_user: FrontendUser


class MessageLLMPayload(BaseModel):
    # id
    user_id: int
    # anger level [0, 1, 2, 3]
    anger_level: int
    # misspelling level [0, 1, 2, 3]
    misspelling_level: int
