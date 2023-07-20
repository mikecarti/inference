from langchain.chains.question_answering import load_qa_chain
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory, ConversationBufferWindowMemory

from src.model.vector_db import VectorDataBase
from src.model import task_manager
from src.model.prompts import PROMPT_TEMPLATE

from loguru import logger
from langchain import OpenAI, LLMChain
from langchain.prompts import PromptTemplate

class Chain:
    def __init__(self, db: VectorDataBase):
        self.chain = self.init_chain()
        self.vector_db: VectorDataBase = db

    async def apredict(self, memory, query):
        manual_part = await self.amanual_search(memory, query)
        response = await self.arun_with_memory(manual_part, memory, query)
        return response

    async def arun_with_memory(self, manual_part, memory: ConversationBufferMemory, query: str):
        await self._set_memory(memory)
        response = await self.chain.arun(manual_part=manual_part, question=query, input_documents=[])
        return response

    async def amanual_search(self, memory, query):
        user_history = await task_manager.acompose_user_history(memory=memory, query=query)

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
            llm=ChatOpenAI(temperature=0, top_p=1, max_tokens=1500),
            memory=ConversationBufferWindowMemory(memory_key="chat_history", input_key="question"),
            prompt=prompt,
            verbose=True,
        )
        return chain

    async def _set_memory(self, memory):
        self.chain.memory = memory
