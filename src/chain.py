from langchain.chains.question_answering import load_qa_chain
from langchain.memory import ConversationBufferMemory

from vector_db import VectorDataBase
import task_manager

from langchain import OpenAI
from langchain.prompts import PromptTemplate

PAID_API_KEY = "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"


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
        manual_part = await self.vector_db.amanual_search(user_history)
        return manual_part

    @staticmethod
    def get_most_similar_result(query, db):
        similar_doc = db.similarity_search_with_score(query)[0][0]
        return similar_doc

    @staticmethod
    def init_chain():
        prompt_template = """
        You are a helpful help desk assistant that tries to answer questions based on context provided.
        If context seems not sufficient to answer a question you must tell that you can not answer this question.
        Make sure that you answer the question.
        Context: {context} {manual_part}
        
        {chat_history}
        
        Question: {question}
        """
        PROMPT = PromptTemplate(
            template=prompt_template, input_variables=['context', 'manual_part', 'question', 'chat_history']
        )

        chain = load_qa_chain(
            llm=OpenAI(temperature=0, max_tokens=500),
            memory=ConversationBufferMemory(memory_key="chat_history", input_key="question"),
            prompt=PROMPT
        )
        return chain

    async def _set_memory(self, memory):
        self.chain.memory = memory
