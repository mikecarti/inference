import os
from typing import List

from loguru import logger

from src.model.chain import SupportBotChain
from src.model.message import AbstractMessage
from src.model.nlu_framework import NLUFramework
from src.model.payload import RetrieveMessageQueuePayload, TowardsFrontendPayload
from src.model.text_transform import TextTransformer
from src.model.db_user.user_db import UserDB
from src.model.utils import wrap
from src.model.db_vector import VectorDataBase
from src.model.db_stat import StatisticsWatcher, StatisticsDB
from src.view.view import View

# TOKENS
os.environ['OPENAI_API_KEY'] = "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"

# Initialize DB and LLMs
user_db = UserDB()
chain = SupportBotChain(vector_knowledge_db=VectorDataBase())
nlu_tool = NLUFramework()
transformer = TextTransformer()

# Initialize Stat Collector
watcher = StatisticsWatcher(stats_db=StatisticsDB())

# Initialize View
view = View()


async def generate_answer(message: AbstractMessage) -> str:
    user_id = message.from_user.id
    user_text = message.text

    memory = user_db.get_memory(user_id)
    answer = await chain.apredict(memory, user_text)

    return view.process_answer(answer)


async def generate_answer_from_llms(message: AbstractMessage) -> (str, str, List):
    """
    :param message:
    :return: Answer, Function_Name, Argument_List
    """
    answer, func_name, args = nlu_tool(message.text, verbose=True)
    if func_name:
        # Answer with function call
        user_db.add_ai_message(ai_message=answer, user_id=message.from_user.id)
        return answer, func_name, args
    else:
        # Answer without function call (regular LLM answer)
        answer = await generate_answer(message)
        return answer, "", []


async def prepare_answer(payload: RetrieveMessageQueuePayload) -> TowardsFrontendPayload:
    """
    Pop first message in queue and create answer on it, then send by a payload.
    :param payload:
    :return:
    """
    message = await user_db.get_from_queue(payload.user_id)
    answer, func_name, args = await generate_answer_from_llms(message)
    answer_with_character = transformer.transform_text(answer, sliders=payload.sliders)

    logger.debug(f"Answer before transforming: {wrap(answer)}")
    logger.debug(f"Answer: {wrap(answer_with_character)}")
    watcher.collect_info(user_message=message, ai_answer=answer)

    return TowardsFrontendPayload(text=answer_with_character, function=func_name, args=args)
