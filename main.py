import asyncio
import logging
import os
from typing import Any

import langchain
from loguru import logger
from aiogram import Bot, Dispatcher, executor, types
from src.model.chain import Chain
from src.model.ocr_checker import ReceiptOCR
from src.model.vector_db import VectorDataBase
from src.model.user_db.user_db import UserDB
from src.model.utils import wrap, init_logging
from src.view.view import View
from src.model.exceptions import InvalidMessageTypeException

# TOKENS
API_TOKEN = '6517253129:AAG9fu1rt-QwFDqOvriLXMgmRURX2nPf8zA' #http://t.me/chizhik_helpdesk_bot

os.environ['OPENAI_API_KEY'] = "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"

# Configure logging
logging.basicConfig(level=logging.INFO)
init_logging()

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Initialize DBs and LLM
user_db = UserDB()
vector_db = VectorDataBase()
chain = Chain(vector_db)
receipt_checker = ReceiptOCR()

# Initialize View
view = View()


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message) -> None:
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    await message.reply("Добрый день!\nЯ сотрудник поддержки, наделенный искусственным интеллектом, как могу помочь вам сегодня?")


@dp.message_handler(commands=['clear'])
async def send_welcome(message: types.Message) -> None:
    user_id = message.from_user.id
    user_db._get(user_id)._reset_memory()
    await message.reply("Память переписки очищена!")


@dp.message_handler(content_types=['text'])
async def add_message_to_queue(message: types.Message) -> None:
    logger.debug(f"Message from user {message.from_user.username} added to queue: <{message.text}>")
    user_id = message.from_user.id
    await user_db.add_to_queue(user_id, message)


async def process_queues() -> None:
    logger.info("Message processing task started")
    sleep_for = 0.3
    while True:
        await asyncio.sleep(sleep_for)
        for user_id in user_db.get_user_ids():
            message = await user_db.get_from_queue(user_id)
            if message:
                await answer_message(message)


@dp.message_handler(content_types=['document'])
async def process_document(message: types.Message) -> None:
    """Processes files sent by user (but not images)"""
    logger.debug(f"File from user {message.from_user.username} is processing")
    doc = message.document
    answer = await receipt_checker.acheck_transactions_status(doc)
    await send_message(message, answer)


async def answer_message(message: types.Message) -> None:
    user_id = message.from_user.id
    user_msg = message.text

    memory = user_db.get_memory(user_id)
    answer = await chain.apredict(memory, user_msg)

    answer = view.process_answer(answer)
    await send_message(message, answer)


async def send_message(user_message: types.Message, bot_answer: str) -> None:
    logger.debug(f"Answer: {wrap(bot_answer)}")
    await user_message.reply(bot_answer)


async def on_startup_launch(args: Any) -> None:
    asyncio.create_task(process_queues())


def main() -> None:
    os.environ["PYTHONASYNCIODEBUG"] = "1"
    # langchain.debug = True
    executor.start_polling(dp, skip_updates=False, on_startup=on_startup_launch)


if __name__ == '__main__':
    main()
