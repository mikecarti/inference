from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.schema import SystemMessage
from loguru import logger

from src.model.prompts import TRANSFORMER_SYSTEM_PROMPT, TRANSFORMER_QUERY_PROMPT


class TextTransformer:
    REQUIRED_SLIDERS = ["anger_level", "misspelling_level"]

    def __init__(self):
        self._llm = ChatOpenAI(model="gpt-3.5-turbo")

    def transform_text(self, text: str, sliders: dict) -> str:
        for req_slider in self.REQUIRED_SLIDERS:
            assert sliders.get(req_slider) is not None
            assert 0 <= sliders.get(req_slider) <= 3

        prompt = self._build_transformation_prompt(question=text, sliders=sliders)
        return self._llm(prompt).content

    def _build_transformation_prompt(self, question: str, sliders: dict) -> list:
        anger_text, misspelling_text = self._convert_sliders_to_text(sliders=sliders)
        prompt = PROMPT.format_messages(question=question, anger_level=anger_text, misspelling_level=misspelling_text)
        logger.debug(f"Prompt after formatting: {prompt[1].content}")
        return prompt

    @staticmethod
    def _convert_sliders_to_text(sliders: dict) -> tuple[str, str]:
        anger_text = ANGER_LEVELS.get(sliders.get('anger'))
        misspelling_text = MISSPELLING_LEVELS.get(sliders.get('misspelling'))

        return anger_text, misspelling_text


PROMPT = ChatPromptTemplate.from_messages(
    [
        SystemMessage(content=TRANSFORMER_SYSTEM_PROMPT),
        HumanMessagePromptTemplate.from_template(TRANSFORMER_QUERY_PROMPT),
    ]
)

ANGER_LEVELS = {
    0: "not aggressive and not rude",
    1: "slightly aggressive and rude",
    2: "aggressive and rude",
    3: "extremely aggressive and rude"
}

MISSPELLING_LEVELS = {
    0: "spelled perfectly correct",
    1: "spelled slightly incorrect",
    2: "spelled mildly incorrect",
    3: "spelled extremely incorrect"
}
