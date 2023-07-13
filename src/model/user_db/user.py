import threading
from dataclasses import dataclass

from langchain.memory import ConversationBufferMemory


@dataclass()
class User:
    memory: ConversationBufferMemory
    id: int | str

    def __init__(self, user_id, name="TestName"):
        self.memory = ConversationBufferMemory(memory_key="chat_history", input_key="question")
        self.id = user_id
        self.name = name
        self.max_time_since_last_query = 60 * 5  # 5 minutes and user is accounted as a user with solved problem
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
