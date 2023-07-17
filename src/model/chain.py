from langchain.chains.question_answering import load_qa_chain
from langchain.memory import ConversationBufferMemory

from src.model.vector_db import VectorDataBase
from src.model import task_manager

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
        prompt_template = """You are a helpful betting company help desk assistant that tries to answer questions 
        based on manual provided. Manual just tells how to solve problems, but sometimes manual problem is not the 
        same as a problem of a person. If context seems not sufficient to answer a question you must tell that you 
        can not answer this question. Else if user question seems not associated with issues, that might occur while 
        placing bets on sports on betting service, refuse to answer and ask if you can help somehow. Speak the same 
        language that the Human speaks. 
        Manual: {context} {manual_part}
        
        {chat_history}
        
        Human question: {question}
        """
        PROMPT = PromptTemplate(
            template=prompt_template, input_variables=['context', 'manual_part', 'question', 'chat_history']
        )

        chain = load_qa_chain(
            llm=OpenAI(temperature=0, max_tokens=500),
            memory=ConversationBufferMemory(memory_key="chat_history", input_key="question"),
            prompt=PROMPT,
            verbose=True,
        )
        return chain

    async def _set_memory(self, memory):
        self.chain.memory = memory
