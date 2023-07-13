from dataclasses import dataclass
from langchain.memory import ConversationBufferMemory
import threading


@dataclass()
class User:
    memory: ConversationBufferMemory
    id: int | str

    def __init__(self, user_id, name="TestName"):
        self.memory = ConversationBufferMemory(memory_key="chat_history", input_key="question")
        self.id = user_id
        self.name = name
        self.max_time_since_last_query = 5  # 5 minutes and user is accounted as a user with solved problem
        self.problem_solved_countdown = threading.Timer(self.max_time_since_last_query, self._reset_memory)
        self.log_resets = False

    def get_memory(self):
        self._reset_countdown()
        return self.memory

    def _reset_countdown(self):
        self.problem_solved_countdown.cancel()
        self.problem_solved_countdown = threading.Timer(self.max_time_since_last_query, self._reset_memory)
        self.problem_solved_countdown.start()

    def _reset_memory(self):
        if self.log_resets:
            print(f"Memory of user {self.id} was reset")
        self.memory = ConversationBufferMemory(memory_key="chat_history", input_key="question")


class UserDB:
    def __init__(self):
        self.db = {}

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

        user = User(user_id=user_id)
        self.db[user_id] = user
        return user

    def _user_exists(self, user_id):
        if self.db.get(user_id):
            return True
        else:
            return False
