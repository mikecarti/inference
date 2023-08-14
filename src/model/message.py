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
