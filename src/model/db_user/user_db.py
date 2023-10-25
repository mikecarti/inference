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
        """
        Add message to message_queue of a given user
        :param user_id:
        :param message:
        :return:
        """
        if not self._user_exists(user_id):
            self._add_user(user_id)
        user = self.db[user_id]
        await user.add_to_queue(message)

    async def get_from_queue(self, user_id: str) -> AbstractMessage:
        """
        Receive oldest message from user's queue
        :param user_id:
        :return:
        """
        if not self._user_exists(user_id):
            raise KeyError(f"User {user_id} is not existing")
        user = self.db[user_id]
        message = await user.get_from_queue()
        return message

    def get_user_ids(self) -> List[str]:
        """
        Get ids of all users
        :return:
        """
        return list(self.db.keys())

    def reset_memory(self, user_id: str) -> None:
        """
        Reset chat memory of a given user.
        :param user_id:
        :return:
        """
        self._get(user_id).reset_memory()

    def get_memory(self, user_id: str) -> ConversationBufferWindowMemory:
        """
        Get chat memory of a given user
        :param user_id:
        :return:
        """
        if self._user_exists(user_id):
            user = self._get(user_id)
        else:
            user = self._add_user(user_id)
        return user.get_memory()

    def add_ai_message(self, ai_message: str, user_id: str) -> str:
        """
        Add ai message to a chat history of a given user.
        :param ai_message:
        :param user_id:
        :return:
        """
        memory = self.get_memory(user_id)
        memory.chat_memory.add_ai_message(ai_message)
        return ai_message

    def _get(self, user_id: str) -> User:
        """
        Get User method.
        :param user_id:
        :return:
        """
        return self.db.get(user_id)

    def _add_user(self, user_id: str) -> User:
        """
        Add a user to database
        :param user_id:
        :return:
        """
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
        """
        Check if user is already in a database
        :param user_id:
        :return:
        """
        if self.db.get(user_id):
            return True
        else:
            return False

    def _init_conversation_memory(self) -> BaseMemory:
        """
        Initialize chat memory for some user.
        :return:
        """
        return ConversationBufferWindowMemory(memory_key="chat_history",
                                              input_key="question",
                                              k=self.store_k_interactions,
                                              human_prefix="User",
                                              ai_prefix="HelpDesk")
