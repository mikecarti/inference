import os
from typing import List

from loguru import logger

from src.model.chain import Chain
from src.model.message import AbstractMessage
from src.model.nlu_framework import NLUFramework
from src.model.payload import RetrieveMessageQueuePayload, TowardsFrontendPayload
from src.model.text_transform import TextTransformer
from src.model.user_db.user_db import UserDB
from src.model.utils import wrap
from src.model.vector_db import VectorDataBase
from src.view.view import View

# TOKENS
os.environ['OPENAI_API_KEY'] = "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"

# Initialize DB and LLMs
user_db = UserDB()
chain = Chain(db=VectorDataBase())
nlu_tool = NLUFramework()
transformer = TextTransformer()

# Initialize View
view = View()



async def generate_answer(message: AbstractMessage) -> str:
    user_id = message.from_user.id
    user_text = message.text

    memory = user_db.get_memory(user_id)
    answer = await chain.apredict(memory, user_text)

    answer = view.process_answer(answer)
    return answer


async def generate_answer_from_llms(message: AbstractMessage) -> (str, str, List):
    """
    :param message:
    :return: Answer, Function_Name, Argument_List
    """
    answer, func_name, args = nlu_tool(message.text, verbose=True)
    if func_name:
        user_db.add_ai_message(ai_message=answer, user_id=message.from_user.id)
        return answer, func_name, args
    answer_no_function = await generate_answer(message)
    return answer_no_function, "", []


async def prepare_answer(payload: RetrieveMessageQueuePayload) -> TowardsFrontendPayload:
    message = await user_db.get_from_queue(payload.user_id)
    answer, func_name, args = await generate_answer_from_llms(message)

    logger.debug(f"Answer before transforming: {wrap(answer)}")
    answer_with_character = transformer.transform_text(answer, sliders=payload.sliders)
    logger.debug(f"Answer: {wrap(answer_with_character)}")
    return TowardsFrontendPayload(text=answer_with_character, function=func_name, args=args)
