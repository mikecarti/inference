from langchain.memory import ConversationBufferWindowMemory

from .user import User
from typing import *


class UserDB:

    def __init__(self):
        self.db = {}
        self.store_k_interactions = 4

    async def add_to_queue(self, user_id, message):
        if not self._user_exists(user_id):
            self._add_user(user_id)
        user = self.db[user_id]
        await user.add_to_queue(message)

    async def get_from_queue(self, user_id):
        if not self._user_exists(user_id):
            raise KeyError(f"User {user_id} is not existing")
        user = self.db[user_id]
        message = await user.get_from_queue()
        return message

    def store_messages(self, user_id, user_msg, ai_msg):
        """
        DEPRECATED
        :param user_id:
        :param user_msg:
        :param ai_msg:
        :return:
        """
        if self._user_exists(user_id):
            user = self._get(user_id)
        else:
            user = self._add_user(user_id)
        user.memory.chat_memory.add_user_message(user_msg)
        user.memory.chat_memory.add_ai_message(ai_msg)

    def notify_queue_message_processed(self, user_id):
        self._get(user_id).task_done()

    def get_user_ids(self) -> List[id]:
        return list(self.db.keys())

    def get_memory(self, user_id):
        if self._user_exists(user_id):
            user = self._get(user_id)
        else:
            user = self._add_user(user_id)
        return user.get_memory()

    def _get(self, user_id) -> User:
        return self.db.get(user_id)

    def _add_user(self, user_id) -> User:
        if self._user_exists(user_id):
            raise Exception("User exists")

        memory = self._init_conversation_memory()
        user = User(user_id=user_id, memory=memory)
        self.db[user_id] = user
        return user

    def _user_exists(self, user_id):
        if self.db.get(user_id):
            return True
        else:
            return False

    def _init_conversation_memory(self):
        return ConversationBufferWindowMemory(memory_key="chat_history",
                                              input_key="question",
                                              k=self.store_k_interactions,
                                              ai_prefix="AI")
