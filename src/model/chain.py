from langchain.chat_models import ChatOpenAI
from langchain import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory, ConversationBufferWindowMemory
from langchain.prompts import PromptTemplate
from langchain.schema import SystemMessage
from loguru import logger

from src.model import prompt_engineer
from src.model.prompts import PROMPT_TEMPLATE
from src.model.tool_executor import ToolExecutor
from src.model.vector_db import VectorDataBase
from src.model.manual_parser import ManualParser


class Chain:
    def __init__(self, db: VectorDataBase):
        self.chain = self.init_chain()
        self.vector_db: VectorDataBase = db
        self.tool_executor = ToolExecutor()
        self.parser = ManualParser()

    async def apredict(self, memory, query):
        manual_part = await self.amanual_search(memory, query)
        manual_text, functions = self.parser.process_manual(manual_part)
        result_of_execution = self.tool_executor.execute_all(functions)
        manual_text = prompt_engineer.fill_info_from_function(manual_text, result_of_execution)
        self._set_llm_reminder(memory)
        response = await self.arun_with_memory(manual_text, memory, query)
        logger.debug(f"Answer: ", response)
        return response

    async def arun_with_memory(self, manual_part, memory: ConversationBufferMemory, query: str):
        await self._set_memory(memory)
        logger.debug(f"Manual after formatting: {manual_part}")
        response = await self.chain.arun(manual_part=manual_part, question=query)
        return response

    @staticmethod
    def _set_llm_reminder(memory):
        # save a reminder
        system_input = SystemMessage(content="Remember to follow 3 steps provided above to answer this question.")
        memory.save_context(system_input)

    async def amanual_search(self, memory, query):
        user_history = await prompt_engineer.acompose_user_history(memory=memory, query=query)

        logger.debug(f"SEARCHING IN VECTOR DB THIS: \n {user_history}")
        manual_part = await self.vector_db.amanual_search(user_history)
        return manual_part

    @staticmethod
    def get_most_similar_result(query, db):
        similar_doc = db.similarity_search_with_score(query)[0][0]
        return similar_doc

    @staticmethod
    def init_chain():
        prompt = PromptTemplate(
            template=PROMPT_TEMPLATE, input_variables=['manual_part', 'question', 'chat_history']
        )

        chain = LLMChain(
            llm=ChatOpenAI(temperature=0, max_tokens=1500),
            memory=ConversationBufferWindowMemory(memory_key="chat_history", input_key="question"),
            prompt=prompt,
            verbose=True,
        )
        return chain

    async def _set_memory(self, memory):
        self.chain.memory = memory
