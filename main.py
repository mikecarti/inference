import asyncio
import logging
import os
import sys

import langchain
from loguru import logger
from src.model.utils import init_logging
from aiogram import Bot, Dispatcher, executor, types
from src.model.chain import Chain
from src.model.vector_db import VectorDataBase
from src.model.user_db.user_db import UserDB
from src.model.utils import wrap, init_logging
from src.view.view import View

# TOKENS
API_TOKEN = '6309821654:AAG2P_3WmwQfoG7hOrhLZDv665nN1IeU4jQ'
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

# Initialize View
view = View()





@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    await message.reply("Hi!\nI'm DeskHelp Bot!")


@dp.message_handler()
async def add_message_to_queue(message: types.Message):
    logger.debug(f"Message from user {message.from_user.username} added to queue: <{message.text}>")
    user_id = message.from_user.id
    await user_db.add_to_queue(user_id, message)


async def process_messages():
    logger.info("Message processing task started")
    sleep_for = 0.0
    while True:
        await asyncio.sleep(sleep_for)
        for user_id in user_db.get_user_ids():
            message = await user_db.get_from_queue(user_id)
            if message:
                await answer_message(message)


@dp.message_handler()
async def answer_message(message: types.Message):
    user_id = message.from_user.id
    user_msg = message.text

    memory = user_db.get_memory(user_id)
    answer = await chain.apredict(memory, user_msg)

    answer = view.process_answer(answer)
    logger.debug(f"Answer: {wrap(answer)}")
    await message.reply(answer)


async def on_startup_launch(args):
    asyncio.create_task(process_messages())

def main():
    os.environ["PYTHONASYNCIODEBUG"] = "1"
    # langchain.debug = True
    executor.start_polling(dp, skip_updates=False, on_startup=on_startup_launch)

if __name__ == '__main__':
    main()
