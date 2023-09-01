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

    @return_with_name
    def cashback_balance(self, x):
        return "5 рублей"

    @return_with_name
    def delivery_status(self, x):
        return "Shipment is being delivered. Will come in 10 minutes"

    @return_with_name
    def wallet_linking(self, x):
        return "Virtual wallet linked successfully"

    @return_with_name
    def document_status(self, x):
        return "Documents are preparing"

    @return_with_name
    def refund_status(self, x):
        return "Refund will be provided in 1 hour"

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
                func=self.cashback_balance,
                description="useful for when you need to answer questions about cashback balance of a user",
            ),
            Tool(
                name="Delivery-Status",
                func=self.delivery_status,
                description="useful for when you need to answer questions about delivery status (where is the current "
                            "delivery, when will it come, etc)",
            ),
            Tool(
                name="Virtual-Wallet",
                func=self.wallet_linking,
                description="useful for when you need to link virtual wallet to user's account"
            ),
            Tool(
                name="Document-Status",
                func=self.document_status,
                description="Check status of documents that were sent to user"
            ),
            Tool(
                name="Refund-Status",
                func=self.refund_status,
                description="Check status of refund for last good that user purchased from our service"
            )
        ]
        return tools
