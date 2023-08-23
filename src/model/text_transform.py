from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.schema import SystemMessage
from loguru import logger

from src.model.prompts import TRANSFORMER_SYSTEM_PROMPT, TRANSFORMER_QUERY_PROMPT, REQUIRED_SLIDERS, LEVELS


class TextTransformer:
    def __init__(self):
        self._llm = ChatOpenAI(model="gpt-3.5-turbo")

    def transform_text(self, text: str, sliders: dict) -> str:
        for req_slider in REQUIRED_SLIDERS:
            assert sliders.get(req_slider) is not None
            assert 0 <= sliders.get(req_slider) <= 3

        prompt = self._build_transformation_prompt(question=text, sliders=sliders)
        return self._llm(prompt).content

    def _build_transformation_prompt(self, question: str, sliders: dict) -> list:
        sliders_text = self._convert_sliders_to_text(sliders=sliders)
        prompt = PROMPT.format_messages(question=question, **sliders_text)
        logger.debug(f"Prompt after formatting: {prompt[1].content}")
        return prompt

    def _convert_sliders_to_text(self, sliders: dict[str, int]) -> dict[str, str]:
        sliders_text = {}
        for slider_name, slider_value in sliders.items():
            value_to_text = LEVELS.get(slider_name)
            sliders_text[slider_name] = value_to_text.get(slider_value)
        return sliders_text


PROMPT = ChatPromptTemplate.from_messages(
    [
        SystemMessage(content=TRANSFORMER_SYSTEM_PROMPT),
        HumanMessagePromptTemplate.from_template(TRANSFORMER_QUERY_PROMPT),
    ]
)
