import logging
import os

from aiogram import Bot, Dispatcher, executor, types
from src.model.chain import Chain
from src.model.vector_db import VectorDataBase
from src.model.user_db.user_db import UserDB
from src.model.utils import wrap
from src.view.view import View

# TOKENS
API_TOKEN = '6309821654:AAG2P_3WmwQfoG7hOrhLZDv665nN1IeU4jQ'
os.environ['OPENAI_API_KEY'] = "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"

# Configure logging
logging.basicConfig(level=logging.INFO)

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
async def answer_message(message: types.Message):
    print(f"\tMessage from user {message.from_user.username}:")
    user_id = message.from_user.id
    user_msg = message.text

    memory = user_db.get_memory(user_id)
    answer = await chain.apredict(memory, user_msg)
    user_db.store_messages(user_id=user_id, user_msg=user_msg, ai_msg=answer)

    answer = view.mock_process_answer(answer)
    print(f"\tAnswer: {wrap(answer)}")
    await message.reply(answer)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
