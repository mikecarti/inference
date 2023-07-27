from langchain.chat_models import ChatOpenAI
from langchain import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory, ConversationBufferWindowMemory
from langchain.prompts import PromptTemplate
from langchain.schema import SystemMessage
from loguru import logger

from src.model.prompt_engineer import fill_info_from_function, acompose_user_history
from src.model.prompts import PROMPT_TEMPLATE
from src.model.tool_executor import ToolExecutor
from src.model.vector_db import VectorDataBase
from src.model.manual_parser import ManualParser
from src.model.relevance import RelevanceModel


class Chain:
    def __init__(self, db: VectorDataBase):
        self.relevance_model = RelevanceModel()
        self.chain = self.init_chain()
        self.vector_db: VectorDataBase = db
        self.tool_executor = ToolExecutor()
        self.parser = ManualParser()

    async def apredict(self, memory, query):
        user_history = await acompose_user_history(memory=memory, query=query)
        manual_part = await self.amanual_search(user_history)
        functions, manual_text = await self.parse_manual(manual_part)
        result_of_execution = await self.execute_functions(functions)
        manual_text = fill_info_from_function(manual_text, result_of_execution)
        response = await self.arun_with_memory(manual_text, memory, query)
        logger.debug(f"Answer: ", response)
        return response

    async def execute_functions(self, functions):
        return self.tool_executor.execute_all(functions)

    async def parse_manual(self, manual_part):
        manual_text, functions = self.parser.process_manual(manual_part)
        return functions, manual_text

    async def arun_with_memory(self, manual_part, memory: ConversationBufferMemory, query: str):
        await self._set_memory(memory)
        logger.debug(f"Manual after formatting: {manual_part}")
        response = await self.chain.arun(manual_part=manual_part, question=query)
        return response

    async def amanual_search(self, messages: list):
        text = ' '.join(messages)
        logger.debug(f"SEARCHING IN VECTOR DB THIS: \n {text}")
        # manual_part = await self.vector_db.amanual_search(user_history)
        manual_part = await self.vector_db.amanual_search(text)
        return manual_part

    async def determine_relevant_part(self, user_history: list) -> list:
        return await self.relevance_model.predict_relevant_part(user_history)

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
