from datetime import datetime
from dataclasses import dataclass


@dataclass()
class FrontendUser:
    id: str
    username: str


@dataclass()
class AbstractMessage:
    text: str
    date: datetime
    from_user: FrontendUser


@dataclass()
class RestApiMessage(AbstractMessage):
    pass


