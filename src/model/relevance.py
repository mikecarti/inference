from typing import List

from langchain import LLMChain, PromptTemplate
from langchain.chat_models import ChatOpenAI
from loguru import logger


class RelevanceModel:
    def __init__(self):
        self.prompt_template = """
        
        """

        self.chain = LLMChain(
            llm=ChatOpenAI(temperature=0),
            prompt=PromptTemplate(template=self.prompt_template, input_variables=[]),
            verbose=True
        )

