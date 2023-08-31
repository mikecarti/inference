import logging
import os
from typing import List

from loguru import logger
from fastapi import FastAPI, HTTPException

from src.model.chain import Chain
from src.model.exceptions import MessageQueueEmptyException, LimitExceededException
from src.model.payload import AddMessageQueuePayload, RetrieveMessageQueuePayload, TowardsFrontendPayload
from src.model.text_transform import TextTransformer
from src.model.user_db.user_db import UserDB
from src.model.utils import wrap, init_logging
from src.model.vector_db import VectorDataBase
from src.model.message import *
from src.model.nlu_framework import NLUFramework
from src.view.view import View

# TOKENS
os.environ['OPENAI_API_KEY'] = "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"

# Configure logging
logging.basicConfig(level=logging.INFO)
init_logging()

# Initialize API
app = FastAPI()

# Initialize DBs and LLM
user_db = UserDB()
chain = Chain(db=VectorDataBase())
nlu_tool = NLUFramework()
transformer = TextTransformer()

# Initialize View
view = View()


@app.post("/add_message")
async def add_message_to_queue(payload: AddMessageQueuePayload) -> None:
    message = RestApiMessage(
        text=payload.text,
        date=payload.date,
        from_user=FrontendUser(
            id=payload.from_user.id,
            username=payload.from_user.username
        )
    )

    logger.debug(f"Message from user {message.from_user.username} added to queue: <{message.text}>")
    user_id = message.from_user.id
    await user_db.add_to_queue(user_id, message)


@app.post("/answer_message")
async def answer_message(payload: RetrieveMessageQueuePayload) -> TowardsFrontendPayload:
    try:
        return await prepare_answer(payload)
    except MessageQueueEmptyException:
        raise HTTPException(status_code=404, detail="Message queue is empty")
    except LimitExceededException:
        raise HTTPException(status_code=429, detail="Spam limit exceeded")
    except Exception as e:
        logger.debug(f"Exception: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def prepare_answer(payload: RetrieveMessageQueuePayload) -> TowardsFrontendPayload:
    message = await user_db.get_from_queue(payload.user_id)
    answer, func_name, args = await generate_answer_from_llms(message)

    logger.debug(f"Answer before transforming: {wrap(answer)}")
    answer_with_character = transformer.transform_text(answer, sliders=payload.sliders)
    logger.debug(f"Answer: {wrap(answer_with_character)}")
    return TowardsFrontendPayload(text=answer_with_character, function=func_name, args=args)


async def generate_answer_from_llms(message: AbstractMessage) -> (str, str, List):
    """
    :param message:
    :return: Answer, Function_Name, Argument_List
    """
    answer, func_name, args = nlu_tool(message.text)
    if func_name:
        return answer, func_name, args
    answer_no_function = await generate_answer(message)
    return answer_no_function, "", []


@app.post("/clear_memory/{user_id}")
async def clear_memory(user_id: int) -> TowardsFrontendPayload:
    user_db.reset_memory(user_id)
    return TowardsFrontendPayload(text="Память переписки очищена!", function="", args=[])


async def generate_answer(message: AbstractMessage) -> str:
    user_id = message.from_user.id
    user_text = message.text

    memory = user_db.get_memory(user_id)
    answer = await chain.apredict(memory, user_text)

    answer = view.process_answer(answer)
    return answer


# alternatively run in console
# uvicorn main:app --host 0.0.0.0 --port 8000
if __name__ == '__main__':
    import uvicorn

    # os.environ["PYTHONASYNCIODEBUG"] = "1"
    uvicorn.run(app, host="0.0.0.0", port=8000)
