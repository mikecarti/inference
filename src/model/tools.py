from typing import List, Dict, Callable
from langchain.agents import Tool


def return_with_name(func) -> (str, List[str]):
    """
    :param func:
    :return: function name and list of output
    """
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        if type(result) != list and type(result) != tuple:
            result = [result]
        result = [str(out) for out in result]
        return func.__name__, result

    return wrapper


class ToolConstructor:
    def __init__(self):
        self.tools = self._construct_tools()

    @return_with_name
    def change_background_color(self, color_hex: str):
        return color_hex

    def _construct_tools(self) -> List[Tool]:
        tools = [
            Tool(
                name="Frontend-Color-Changer",
                func=self.change_background_color,
                description="useful for when you need to change color of website or background. write in hexadecimal "
                            "representation of color"
            ),
            Tool(
                name="Cashback-Balance",
                func=lambda x: "5 рублей",
                description="useful for when you need to answer questions about cashback balance of a user",
            ),
            Tool(
                name="Delivery-Status",
                func=lambda x: "Shipment is being delivered. Will come in 10 minutes",
                description="useful for when you need to answer questions about delivery status (where is the current "
                            "delivery, when will it come, etc)",
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
