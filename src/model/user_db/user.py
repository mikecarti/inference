import asyncio
import copy
import datetime
import threading
from dataclasses import dataclass
from typing import List
from langchain.memory import ConversationBufferWindowMemory
from langchain.schema import BaseMemory
from src.model.exceptions import MessageQueueEmptyException, LimitExceededException
from loguru import logger

from src.model.message import AbstractMessage


@dataclass()
class User:
    memory: ConversationBufferWindowMemory
    id_: int | str

    def __init__(self, user_id: id, memory: BaseMemory, memory_life_time_seconds: int, spam_msg_wait_time_seconds: int,
                 name: str = "TestName"):
        self._empty_memory = copy.deepcopy(memory)
        self.memory = memory
        self.id_ = user_id
        self.name = name
        self.memory_life_time_seconds = memory_life_time_seconds
        self._spam_msg_wait_time_seconds = spam_msg_wait_time_seconds
        self.problem_solved_countdown = threading.Timer(self.memory_life_time_seconds, self.reset_memory)
        self.message_queue = asyncio.Queue()
        self.log_resets = False

    def get_memory(self) -> BaseMemory:
        self._reset_countdown()
        return self.memory

    def reset_memory(self) -> None:
        if self.log_resets:
            logger.debug(f"Memory of user {self.id_} was reset")
        self.memory = copy.deepcopy(self._empty_memory)

    def task_done(self) -> None:
        self.message_queue.task_done()

    def _reset_countdown(self) -> None:
        self.problem_solved_countdown.cancel()
        self.problem_solved_countdown = threading.Timer(self.memory_life_time_seconds, self.reset_memory)
        self.problem_solved_countdown.start()

    async def add_to_queue(self, message):
        print(f"Message added to queue for user {self.id_}, {self.name}: {message.text}")
        await self.message_queue.put(message)

    async def get_from_queue(self):
        try:
            last_message = await asyncio.wait_for(self.message_queue.get(), timeout=self._spam_msg_wait_time_seconds)
            if self._user_sent_message_recently(last_message):
                raise LimitExceededException(f"Spam prevention for user {self.id_}, {self.name}")
            message = await self._collect_message_from_recent_messages(last_message)
            return message
        except asyncio.TimeoutError:
            raise MessageQueueEmptyException(
                f"Queue of user {self.id_}, {self.name} empty. Either user messages are being summarized or an answer was requested without adding a user message to the queue")

    async def _collect_message_from_recent_messages(self, last_message):
        messages = [last_message.text]
        while True:
            try:
                message = await asyncio.wait_for(self.message_queue.get(), timeout=self._spam_msg_wait_time_seconds)
                if self._sufficient_time_difference(last_message.date, message.date):
                    break
                messages.append(message.text)
            except asyncio.TimeoutError:
                break
        return last_message._replace(text=" ".join(messages))

    def _user_sent_message_recently(self, last_message):
        now = datetime.datetime.now()
        return not self._sufficient_time_difference(last_message.date, now, self._spam_msg_wait_time_seconds)

    @staticmethod
    def _sufficient_time_difference(dt1, dt2, threshold):
        time_difference = dt2 - dt1
        return abs(time_difference.total_seconds()) > threshold
