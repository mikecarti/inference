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
    """
    Big portion of this class addresses anti-spam issues, that is written in non-obvious way.
    """
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

    def get_memory(self) -> ConversationBufferWindowMemory:
        """
        Get chat memory of a current user
        :return:
        """
        self._reset_memory_countdown()
        return self.memory

    async def add_to_queue(self, message: AbstractMessage) -> None:
        """
        Add message to user's queue
        :param message:
        :return:
        """
        # this method may be blocking if queue has element number limit
        print("Message added to q: ", message.text)
        await self.message_queue.put(message)

    async def get_from_queue(self) -> AbstractMessage:
        """
        Pop message from queue.
        :return:
        """
        self.check_queue_emptiness()
        if self._user_sent_message_recently():
            sys_msg = f"Spam prevention for user {self.id_, self.name}"
            logger.debug(sys_msg)
            raise LimitExceededException(sys_msg)
        message = await self._collect_message_from_recent_messages()
        return message

    def reset_memory(self) -> None:
        """
        Empty user's memory
        :return:
        """
        if self.log_resets:
            logger.debug(f"Memory of user {self.id_} was reset")
        self.memory = copy.deepcopy(self._empty_memory)

    def _reset_memory_countdown(self) -> None:
        """
        Reset countdown of memory timer
        :return:
        """
        self.problem_solved_countdown.cancel()
        self.problem_solved_countdown = threading.Timer(self.memory_life_time_seconds, self.reset_memory)
        self.problem_solved_countdown.start()

    async def _collect_message_from_recent_messages(self) -> AbstractMessage:
        """
        Connect last messages in queue, that were spammed into one to prevent spamming
        :return:
        """
        prev_q_size = -1
        # while messages keep coming, collect messages
        last_message, messages = None, []
        while self.message_queue.qsize() != prev_q_size:
            prev_q_size = self.message_queue.qsize()
            last_message, message_queue, messages = self._collect_time_close_messages()
            time_elapsed = (datetime.datetime.now() - last_message.date).total_seconds()
            time_to_wait = self._spam_msg_wait_time_seconds - time_elapsed
            await asyncio.sleep(time_to_wait)
        # extract messages from queue
        for _ in range(self.message_queue.qsize()):
            self.message_queue.get_nowait()
        # connect messages
        last_message.text = " ".join(messages)
        return last_message

    def _collect_time_close_messages(self) -> (AbstractMessage, asyncio.Queue, List[AbstractMessage]):
        """
        Collect messages that were spammed.
        :return: (AbstractMessage, asyncio.Queue, List[AbstractMessage])
        """
        message_queue = self.check_queue_emptiness()
        last_message = message_queue[-1]
        prev_msg = message_queue[0]  # trick
        messages = []
        # collect messages until long break or until no more messages left
        for msg in message_queue:
            if self._sufficient_time_difference(prev_msg.date, msg.date):
                break
            prev_msg = msg
            messages.append(msg.text)
        return last_message, message_queue, messages

    def check_queue_emptiness(self) -> list:
        """
        Checks if message queue is empty
        :return:
        """
        if self.message_queue.empty():
            sys_msg = f"Queue of user {self.id_, self.name} empty"
            logger.debug(sys_msg)
            raise MessageQueueEmptyException(sys_msg)
        else:
            return self.message_queue._queue

    def _user_sent_message_recently(self) -> bool:
        """
        Checks if user sent message recently
        :return:
        """
        if self.message_queue.empty():
            return False
        last_message: AbstractMessage = self.message_queue._queue[0]
        now = datetime.datetime.now()
        last_message_dt = last_message.date
        return not self._sufficient_time_difference(last_message_dt, now)

    def _sufficient_time_difference(self, dt1: datetime.datetime, dt2: datetime.datetime) -> bool:
        """
        Check if messages are being spammed or not
        :param dt1:
        :param dt2:
        :return:
        """
        time_difference = dt2 - dt1
        enough_time_passed = abs(time_difference.total_seconds()) > self._spam_msg_wait_time_seconds
        return enough_time_passed
