from vector_db import VectorDataBase

from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate

PAID_API_KEY = "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"


class Chain:
    def __init__(self, db: VectorDataBase):
        self.chain = self.init_chain()
        self.vector_db = db

    async def predict(self, query):
        manual_part = await self.vector_db.amanual_search(query)
        response = await self.chain.arun(manual_part=manual_part, question=query)
        return response

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
        Context: {manual_part}
        Question: {question}
        """
        PROMPT = PromptTemplate(
            template=prompt_template, input_variables=['manual_part', 'question']
        )

        chain = LLMChain(
            llm=ChatOpenAI(temperature=0, max_tokens=500), prompt=PROMPT)
        return chain
