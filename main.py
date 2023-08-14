import logging
import os
from loguru import logger
from fastapi import FastAPI, HTTPException

from src.model.chain import Chain
from src.model.ocr_checker import ReceiptOCR
from src.model.user_db.user_db import UserDB
from src.model.utils import wrap, init_logging
from src.model.vector_db import VectorDataBase
from src.model.message import RestApiMessage, MessagePayload, AbstractMessage, FrontendUser
from src.view.view import View

# TOKENS
os.environ['OPENAI_API_KEY'] = "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"

# Configure logging
logging.basicConfig(level=logging.INFO)
init_logging()

# Initialize bot and dispatcher
app = FastAPI()

# Initialize DBs and LLM
user_db = UserDB()
vector_db = VectorDataBase()
chain = Chain(vector_db)
receipt_checker = ReceiptOCR()

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
async def answer_message(data: dict):
    message = await user_db.get_from_queue(data["user_id"])
    if not message:
        return {}

    answer = await generate_answer(message)
    logger.debug(f"Answer: {wrap(answer)}")
    return {"text": answer}


async def generate_answer(message: AbstractMessage) -> str:
    user_id = message.from_user.id
    user_msg = message.text

    memory = user_db.get_memory(user_id)
    answer = await chain.apredict(memory, user_msg)

    answer = view.process_answer(answer)
    return answer


if __name__ == '__main__':
    import uvicorn
    # os.environ["PYTHONASYNCIODEBUG"] = "1"
    uvicorn.run(app, host="0.0.0.0", port=8000)
