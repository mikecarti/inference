from langchain.agents import initialize_agent, Tool
from langchain.agents import AgentType
from langchain.chat_models import ChatOpenAI
from loguru import logger

from typing import List


class NLUFramework:
    def __init__(self):
        llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-0613")
        tools = self._construct_tools()
        self.agent = initialize_agent(tools, llm, agent=AgentType.OPENAI_FUNCTIONS, verbose=True, return_intermediate_steps=True)

    def __call__(self, text) -> str | None:
        agent_response = self.agent(text)
        output = self._get_one_func_chain_output(agent_response)
        return output

    @staticmethod
    def _get_one_func_chain_output(agent_response: dict) -> str | None:
        intermediate_steps = agent_response.get("intermediate_steps")
        # print("agent_response: ", agent_response)
        if not intermediate_steps or len(intermediate_steps) == 0:
            logger.debug("Intent is not recognized")
            return None
        function_output = intermediate_steps[0][1]
        logger.debug(f"Intent is recognized, function output: {function_output}")
        return function_output

    @staticmethod
    def _construct_tools() -> List[Tool]:
        tools = [
            Tool(
                name="Cashback-Balance",
                func=lambda x: "5 рублей",
                description="useful for when you need to answer questions about cashback balance of a user",
            ),
            Tool(
                name="Delivery-Status",
                func=lambda x: "Shipment is being delivered. Will come in 10 minutes",
                description="useful for when you need to answer questions about delivery status (where is the current delivery, when will it come, etc)",
            ),
            Tool(
                name="Virtual-Wallet",
                func=lambda x: "Virtual wallet linked successfully",
                description="useful for when you need to link virtual wallet to user's account"
            ),
            Tool(
                name="Document-Status",
                func=lambda x: "Documents are preparing",
                description="Check status of documents that were sent to user"
            ),
            Tool(
                name="Refund-Status",
                func=lambda x: "Refund will be provided in 1 hour",
                description="Check status of refund for last good that user purchased from our service"
            )
        ]
        return tools
