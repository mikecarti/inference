from langchain.agents import initialize_agent, Tool
from langchain.agents import AgentType
from langchain.chat_models import ChatOpenAI
from loguru import logger
from src.model.tools import ToolConstructor

from typing import List, Tuple


class NLUFramework:
    def __init__(self):
        llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-0613")
        tools = ToolConstructor().tools
        self.agent = initialize_agent(tools, llm, agent=AgentType.OPENAI_FUNCTIONS, verbose=True,
                                      return_intermediate_steps=True)

    def __call__(self, text) -> (str, str, List):
        agent_response = self.agent(text)
        function_name, func_output = self._get_one_func_chain_output(agent_response)
        text = f"Функция {function_name} вызвана!"
        return text, function_name, func_output

    @staticmethod
    def _get_one_func_chain_output(agent_response: dict) -> Tuple[str, List] | Tuple[None, None]:
        intermediate_steps = agent_response.get("intermediate_steps")
        # print("agent_response: ", agent_response)
        if not intermediate_steps or len(intermediate_steps) == 0:
            logger.debug("Intent is not recognized")
            return None, None
        function_output = intermediate_steps[0][1]
        logger.debug(f"Intent is recognized, function output: {function_output}")
        return function_output

