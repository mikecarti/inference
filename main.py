import logging
import os
from loguru import logger
from fastapi import FastAPI, HTTPException

from src.model.chain import Chain
from src.model.exceptions import MessageQueueEmptyException, LimitExceededException
from src.model.text_transform import TextTransformer
from src.model.user_db.user_db import UserDB
from src.model.utils import wrap, init_logging
from src.model.vector_db import VectorDataBase
from src.model.message import RestApiMessage, MessagePayload, AbstractMessage, FrontendUser, MessageLLMPayload
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
async def add_message_to_queue(payload: MessagePayload) -> None:
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
async def answer_message(payload: MessageLLMPayload) -> dict:
    try:
        return await prepare_answer(payload)
    except MessageQueueEmptyException:
        raise HTTPException(status_code=404, detail="Message queue is empty")
    except LimitExceededException:
        raise HTTPException(status_code=429, detail="Spam limit exceeded")
    except Exception as e:
        logger.debug(f"Exception: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def prepare_answer(payload: MessageLLMPayload) -> dict:
    message = await user_db.get_from_queue(payload.user_id)
    answer = process_intents(message)
    if not answer:
        answer = await generate_answer(message)
    logger.debug(f"Answer before transforming: {wrap(answer)}")

    answer = transformer.transform_text(
        answer,
        sliders=payload.sliders
    )
    logger.debug(f"Answer: {wrap(answer)}")
    return {"text": answer}


@app.post("/clear_memory/{user_id}")
async def clear_memory(user_id: int) -> dict:
    user_db.reset_memory(user_id)
    return {"text": "Память переписки очищена!"}


async def generate_answer(message: AbstractMessage) -> str:
    user_id = message.from_user.id
    user_text = message.text

    memory = user_db.get_memory(user_id)
    answer = await chain.apredict(memory, user_text)

    answer = view.process_answer(answer)
    return answer


def process_intents(message: AbstractMessage) -> str:
    return nlu_tool.run(query=message.text)


# alternatively run in console
# uvicorn main:app --host 0.0.0.0 --port 8000
if __name__ == '__main__':
    import uvicorn

    # os.environ["PYTHONASYNCIODEBUG"] = "1"
    uvicorn.run(app, host="0.0.0.0", port=8000)
