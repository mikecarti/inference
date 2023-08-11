import asyncio
import copy
import datetime
import threading
from dataclasses import dataclass

from langchain.memory import ConversationBufferWindowMemory
from langchain.schema import BaseMemory
from aiogram import types
from loguru import logger


@dataclass()
class AbstractMessage:
    text: str
    date: datetime.datetime


@dataclass()
class User:
    memory: ConversationBufferWindowMemory
    id: int | str

    def __init__(self, user_id, memory, memory_life_time_seconds, spam_msg_wait_time_seconds, name="TestName"):
        self._empty_memory = copy.deepcopy(memory)
        self.memory = memory
        self.id = user_id
        self.name = name
        self.memory_life_time_seconds = memory_life_time_seconds
        self._spam_msg_wait_time_seconds = spam_msg_wait_time_seconds
        self.problem_solved_countdown = threading.Timer(self.memory_life_time_seconds, self.reset_memory)
        self.message_queue = asyncio.Queue()
        self.log_resets = False

    def get_memory(self) -> BaseMemory:
        self._reset_countdown()
        return self.memory

    async def add_to_queue(self, message: AbstractMessage) -> None:
        # this method may be blocking if queue has element number limit
        print("Message added to q: ", message.text)
        await self.message_queue.put(message)

    async def get_from_queue(self) -> types.Message | None:
        if self.message_queue.empty():
            return None
        if self._user_sent_message_recently():
            return None
        message = self._collect_message_from_recent_messages()
        return message

    def reset_memory(self):
        if self.log_resets:
            logger.debug(f"Memory of user {self.id} was reset")
        self.memory = copy.deepcopy(self._empty_memory)

    def task_done(self):
        self.message_queue.task_done()

    def _reset_countdown(self):
        self.problem_solved_countdown.cancel()
        self.problem_solved_countdown = threading.Timer(self.memory_life_time_seconds, self.reset_memory)
        self.problem_solved_countdown.start()

    def _collect_message_from_recent_messages(self) -> types.Message:
        message_queue = self.message_queue._queue
        last_message = message_queue[-1]
        prev_msg = message_queue[0]  # trick
        messages = []
        # collect messages until long break or until no more messages left
        for msg in message_queue:
            dt = prev_msg.date - msg.date
            print(f"Previous msg:{prev_msg.text} \nCurrent msg: {msg.text} \n Difference in time: {dt.total_seconds()}")
            if self._sufficient_time_difference(prev_msg.date, msg.date):
                break
            prev_msg = msg
            messages.append(msg.text)
        for _ in range(len(message_queue)):
            self.message_queue.get_nowait()

        # connect messages
        last_message.text = " ".join(messages)
        return last_message

    def _user_sent_message_recently(self):
        if self.message_queue.empty():
            return False
        last_message: AbstractMessage = self.message_queue._queue[0]
        now = datetime.datetime.now()
        last_message_dt = last_message.date
        return not self._sufficient_time_difference(last_message_dt, now)

    def _sufficient_time_difference(self, dt1, dt2):
        time_difference = dt2 - dt1
        enough_time_passed = abs(time_difference.total_seconds()) > self._spam_msg_wait_time_seconds
        return enough_time_passed
