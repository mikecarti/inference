from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage


async def acompose_user_history(memory: ConversationBufferMemory, query: str) -> str:
    history_messages = memory.load_memory_variables({}).get('history')
    if not history_messages:
        history_messages = []
    human_messages = [msg for msg in history_messages if type(msg) is HumanMessage]
    human_messages = [msg.content for msg in human_messages]
    all_human_messages = human_messages + [query]

    return "\n".join(all_human_messages)


def fill_info_from_function(manual_text: str, result_of_execution: str | int) -> str:
    if not result_of_execution:
        return manual_text
    return manual_text.format(function_result=str(result_of_execution))
