from typing import Type

from langchain.chains import LLMChain
from langchain.chains.base import Chain
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import PromptTemplate
from langchain.schema import BaseMemory
from loguru import logger

from src.model.prompts import HELPDESK_PROMPT_TEMPLATE
from src.model.db_vector import VectorDataBase


class KnowledgeChain:
    """
    Main LLM chain, that has access to vector knowledge base.
    """

    def __init__(self, vector_knowledge_db: VectorDataBase):
        self.chain: Type[Chain] = self.init_chain()
        self.vector_db: VectorDataBase = vector_knowledge_db
        self.k_closest_results: int = 10

    async def apredict(self, memory: Type[BaseMemory], query: str) -> str:
        """
        Asynchronous answer generation. 
        :param memory: 
        :param query: 
        :return: 
        """
        manual_part = await self.amanual_search(query, k=self.k_closest_results)
        response = await self._arun_with_memory(manual_part, memory, query)
        logger.debug(f"Answer: ", response)
        return response

    async def _arun_with_memory(self, manual_part: str, memory: Type[BaseMemory], query: str) -> str:
        """
        Asynchronously generate text including memory in history.
        :param manual_part: 
        :param memory: 
        :param query: 
        :return: 
        """
        await self._set_memory(memory)
        # logger.debug(f"Manual after formatting: {manual_part}")
        response = await self.chain.arun(manual_part=manual_part, question=query)
        return response

    async def amanual_search(self, query: str, k: int) -> str:
        """
        Search manual (Knowledge Base) for similar documents.
        :param query: find most similar document to this query
        :param k: k nearest documents in knowledge base
        :return: 
        """
        logger.debug(f"SEARCHING IN VECTOR DB THIS: \n {query}")
        manual_part = await self.vector_db.amanual_search([query], k_nearest=k)
        return manual_part

    @staticmethod
    def init_chain() -> Type[Chain]:
        """
        Initialize a LLM chain
        :return:
        """
        prompt = PromptTemplate(
            template=HELPDESK_PROMPT_TEMPLATE, input_variables=['manual_part', 'question', 'chat_history']
        )

        chain = LLMChain(
            llm=ChatOpenAI(temperature=0, max_tokens=1500, model='gpt-3.5-turbo-16k'),
            memory=ConversationBufferWindowMemory(memory_key="chat_history", input_key="question"),
            prompt=prompt,
            verbose=False,
        )
        return chain

    async def _set_memory(self, memory: Type[BaseMemory]):
        """
        Set current memory as memory for a given user, may be troublesome because class works asynchronously, thus for high loads
        of users, memory may sometimes be placed in other users' dialogues.
        :param memory: 
        :return: 
        """
        self.chain.memory = memory
