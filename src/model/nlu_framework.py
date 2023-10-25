from langchain.agents import initialize_agent, Tool
from langchain.agents import AgentType
from langchain.chat_models import ChatOpenAI
from loguru import logger
from src.model.func_tools import ToolConstructor

from typing import List, Tuple


class NLUFramework:
    def __init__(self):
        llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-0613", max_tokens=500)
        tools: List[Tool] = ToolConstructor().tools
        self.agent = initialize_agent(tools, llm, agent=AgentType.OPENAI_FUNCTIONS, verbose=True,
                                      return_intermediate_steps=True)
        self.suffix = "\nТы обязан ответить на это не более чем 20 словами"

    def __call__(self, text: str, verbose=False) -> (str, str, List):
        """
        Main method of class.
        :param text:
        :param verbose:
        :return:
        """
        logger.debug(f"NLU Processing for text: {text}")

        agent_response = self.agent(text + self.suffix)
        function_name, func_output = self._get_one_func_chain_output(agent_response)

        logger.debug(f"Function: {function_name},\n"
                     f"Function output: {func_output},\n"
                     f"agent_response: {agent_response}")

        if function_name != "":
            output_text = f"Функция {function_name} вызвана!"
        else:
            output_text = ""
        return output_text, function_name, func_output

    @staticmethod
    def _get_one_func_chain_output(agent_response: dict) -> Tuple[str, List]:
        """
        Retrieve only function results, skip LLM Text Generation.
        :param agent_response:
        :return:
        """
        intermediate_steps = agent_response.get("intermediate_steps")
        if not intermediate_steps or len(intermediate_steps) == 0:
            logger.debug("Intent is not recognized")
            return "", []
        function_output = intermediate_steps[0][1]
        function_name = function_output[0]
        function_outputs = function_output[1]

        logger.debug(f"Intent is recognized, function output: {function_output}")
        return function_name, function_outputs
