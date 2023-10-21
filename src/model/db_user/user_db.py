from langchain.memory import ConversationBufferWindowMemory
from langchain.schema import BaseMemory

from src.model.message import AbstractMessage
from src.model.db_user.user import User
from typing import *

from src.model.exceptions import UserExistsException


class UserDB:

    def __init__(self):
        self.db = {}
        self.anti_spam_msg_wait_seconds = 0
        self.store_k_interactions = 2
        self.memory_life_time_seconds = 60 * 3

    async def add_to_queue(self, user_id: str, message: AbstractMessage) -> None:
        if not self._user_exists(user_id):
            self._add_user(user_id)
        user = self.db[user_id]
        await user.add_to_queue(message)

    async def get_from_queue(self, user_id: str) -> AbstractMessage:
        if not self._user_exists(user_id):
            raise KeyError(f"User {user_id} is not existing")
        user = self.db[user_id]
        message = await user.get_from_queue()
        return message

    def notify_queue_message_processed(self, user_id: str) -> None:
        self._get(user_id).task_done()

    def get_user_ids(self) -> List[id]:
        return list(self.db.keys())

    def reset_memory(self, user_id: str) -> None:
        self._get(user_id).reset_memory()

    def get_memory(self, user_id: str) -> ConversationBufferWindowMemory:
        if self._user_exists(user_id):
            user = self._get(user_id)
        else:
            user = self._add_user(user_id)
        return user.get_memory()

    def add_ai_message(self, ai_message: str, user_id: str) -> str:
        memory = self.get_memory(user_id)
        memory.chat_memory.add_ai_message(ai_message)
        return ai_message

    def _get(self, user_id: str) -> User:
        return self.db.get(user_id)

    def _add_user(self, user_id: str) -> User:
        if self._user_exists(user_id):
            raise UserExistsException(f"User {user_id} exists")

        memory = self._init_conversation_memory()
        user = User(user_id=user_id,
                    memory_life_time_seconds=self.memory_life_time_seconds,
                    spam_msg_wait_time_seconds=self.anti_spam_msg_wait_seconds,
                    memory=memory)
        self.db[user_id] = user
        return user

    def _user_exists(self, user_id: str) -> bool:
        if self.db.get(user_id):
            return True
        else:
            return False

    def _init_conversation_memory(self) -> BaseMemory:
        return ConversationBufferWindowMemory(memory_key="chat_history",
                                              input_key="question",
                                              k=self.store_k_interactions,
                                              human_prefix="User",
                                              ai_prefix="HelpDesk")
