import cProfile
import logging
import traceback

from fastapi import FastAPI, HTTPException
from loguru import logger

from src.controller.controller import prepare_answer, user_db
from src.model.exceptions import MessageQueueEmptyException, LimitExceededException
from src.model.payload import AddMessageQueuePayload, RetrieveMessageQueuePayload, TowardsFrontendPayload
from src.model.utils import init_logging, get_random_hint


# Initialize API
app = FastAPI()


@app.post("/add_message")
async def add_message_to_queue(payload: AddMessageQueuePayload) -> None:
    message = payload.to_user_message()

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
        logger.debug(f"Exception: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/get_hint/{user_id}")
async def get_hint(user_id: str) -> TowardsFrontendPayload:
    hint = get_random_hint()
    user_db.add_ai_message(ai_message=hint, user_id=user_id)
    return TowardsFrontendPayload(text=hint, function="", args=[])


@app.post("/clear_memory/{user_id}")
async def clear_memory(user_id: str) -> TowardsFrontendPayload:
    user_db.reset_memory(user_id)
    return TowardsFrontendPayload(text="Память переписки очищена!", function="", args=[])


def main():
    import uvicorn
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    init_logging()

    # os.environ["PYTHONASYNCIODEBUG"] = "1"
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == '__main__':
    main()
    # cProfile.run("main()", sort="cumtime")
