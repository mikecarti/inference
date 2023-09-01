from typing import List, Callable
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
        # function = (Callable, Description)
        functions_with_description = [
            (self.change_background_color, "Useful for changing website or background color. Input in hexadecimal."),
            (self.cashback_balance, "Useful for answering questions about a user's cashback balance."),
            (self.delivery_status, "Useful for answering questions about delivery status (current location, ETA, etc)."),
            (self.wallet_linking, "Useful for linking a virtual wallet to a user's account."),
            (self.document_status, "Checks the status of documents sent to a user."),
            (self.refund_status, "Checks the status of a refund for the last item purchased by a user.")
        ]
        tools = [self._make_tool(*func_tuple) for func_tuple in functions_with_description]
        return tools

    @staticmethod
    def _make_tool(function: Callable, description: str):
        tool = Tool(
            name=function.__name__,
            func=function,
            description=description
        )
        return tool
