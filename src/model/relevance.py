from typing import List

from langchain import LLMChain, PromptTemplate
from langchain.chat_models import ChatOpenAI
from loguru import logger


class RelevanceModel:
    def __init__(self):
        self.prompt_template = """
        Ты интеллектуальная машина-проверщик, 
        
        На вход тебе будет дан список сообщений человека.
        Твоя задача - определить верно ли, что новое сообщение не относится к предыдущим запросам.
        Ответом должно быть булевое значение 1 (не относится) или 0ё (относится).
        
        Пример 1:
        История сообщений:
        Как поставить аватарку? ; Я потерял свой телефон что делать? ; Не приходит смс 
        Новое сообщение:
        Забыл свой пароль телефона
        
        Ответ:0
        
        Пример 2:
        История сообщений:
        Я забыл пароль, что мне делать?
        Новое сообщение:
        Вот я не знаю просто даже как этот пароль восстановить теперь
        
        Ответ:1
        
        Начали!
        История сообщений: 
        {old_messages}
        Новое сообщение:
        {new_message}
    
        Ответ:
        """
        self.chain = LLMChain(
            llm=ChatOpenAI(temperature=0),
            prompt=PromptTemplate(template=self.prompt_template, input_variables=["old_messages", 'new_message']),
            verbose=True
        )

    async def predict_relevant_part(self, user_history: list) -> list:
        if len(user_history) <= 1:
            return user_history

        message_refers_to_new_problem = await self._run(user_history)
        logger.debug(f"Result of relevance model: {message_refers_to_new_problem}")
        if message_refers_to_new_problem:
            return user_history[-1:]
        else:
            return user_history

    async def _run(self, user_history: List[str]) -> bool:
        old_messages = user_history[:-1]
        old_messages = '; '.join(old_messages)
        new_message = user_history[-1]
        result = None
        while result not in ("0", "1"):
            if result:
                logger.debug(
                    f"Retrying with output: {result}, \nOld messages: {old_messages} \nNew message: {new_message}")
            result = self.chain.run(old_messages=old_messages, new_message=new_message)
        return bool(result)
