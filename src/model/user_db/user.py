import asyncio
import copy
import threading
from asyncio import QueueEmpty
from dataclasses import dataclass
from loguru import logger
from langchain.memory import ConversationBufferMemory, ConversationBufferWindowMemory


@dataclass()
class AbstractMessage:
    text: str


@dataclass()
class User:
    memory: ConversationBufferWindowMemory
    id: int | str

    def __init__(self, user_id, memory, memory_life_time_seconds, name="TestName"):
        self._empty_memory = copy.deepcopy(memory)
        self.memory = memory
        self.id = user_id
        self.name = name
        self.memory_life_time_seconds = memory_life_time_seconds  # seconds and user is accounted as a user with solved problem
        self.problem_solved_countdown = threading.Timer(self.memory_life_time_seconds, self._reset_memory)
        self.message_queue = asyncio.Queue()
        self.log_resets = False

    def get_memory(self):
        self._reset_countdown()
        return self.memory

    async def add_to_queue(self, message: AbstractMessage):
        # this method may be blocking if queue has element number limit
        await self.message_queue.put(message)

    async def get_from_queue(self):
        try:
            message = self.message_queue.get_nowait()
        except QueueEmpty:
            message = None
        return message

    def _reset_countdown(self):
        self.problem_solved_countdown.cancel()
        self.problem_solved_countdown = threading.Timer(self.memory_life_time_seconds, self._reset_memory)
        self.problem_solved_countdown.start()

    def _reset_memory(self):
        if self.log_resets:
            logger.debug(f"Memory of user {self.id} was reset")
        self.memory = copy.deepcopy(self._empty_memory)

    def task_done(self):
        self.message_queue.task_done()
