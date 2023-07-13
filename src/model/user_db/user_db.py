from langchain.memory import ConversationBufferWindowMemory

from .user import User

class UserDB:
    def __init__(self):
        self.db = {}
        self.store_k_interactions = 4

    def store_messages(self, user_id, user_msg, ai_msg):
        if self._user_exists(user_id):
            user = self._get(user_id)
        else:
            user = self._add_user(user_id)
        user.memory.chat_memory.add_user_message(user_msg)
        user.memory.chat_memory.add_ai_message(ai_msg)

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

        memory = ConversationBufferWindowMemory(memory_key="chat_history", input_key="question", k=self.store_k_interactions)
        user = User(user_id=user_id, memory=memory)
        self.db[user_id] = user
        return user

    def _user_exists(self, user_id):
        if self.db.get(user_id):
            return True
        else:
            return False
