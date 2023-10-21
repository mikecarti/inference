from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.schema import SystemMessage
from loguru import logger

from src.model.prompts import TRANSFORMER_SYSTEM_PROMPT, TRANSFORMER_QUERY_PROMPT, REQUIRED_SLIDERS, LEVELS


class TextMoodTransformer:
    def __init__(self):
        self._llm = ChatOpenAI(model="gpt-3.5-turbo", max_tokens=700)
        self.PROMPT = ChatPromptTemplate.from_messages(
            [
                SystemMessage(content=TRANSFORMER_SYSTEM_PROMPT),
                HumanMessagePromptTemplate.from_template(TRANSFORMER_QUERY_PROMPT),
            ]
        )

    def transform_text(self, text: str, sliders: dict) -> str:
        """
        Transforms text based on sliders (usually mood or text features)
        :param text:
        :param sliders: transformation parameters
        :return:
        """
        for req_slider in REQUIRED_SLIDERS:
            assert sliders.get(req_slider) is not None, "Slider-names received differ with slider-names written in " \
                                                        "prompts.py for slider: " + str(req_slider)
            assert 0 <= sliders.get(req_slider) <= 3, f"Index of slider is out of range: {sliders.get(req_slider)}"

        if self._sliders_are_default(sliders):
            return text

        prompt = self._build_transformation_prompt(text=text, sliders=sliders)
        return self._llm(prompt).content

    def _build_transformation_prompt(self, text: str, sliders: dict) -> list:
        """
        :param text:
        :param sliders: transformation parameters
        :return:
        """
        sliders_text = self._convert_sliders_to_text(sliders=sliders)
        prompt = self.PROMPT.format_messages(question=text, **sliders_text)
        logger.debug(f"Prompt after formatting: {prompt[1].content}")
        return prompt

    @staticmethod
    def _convert_sliders_to_text(sliders: dict[str, int]) -> dict[str, str]:
        """
        :param sliders: transformation parameters
        :return: plain text
        """
        sliders_text = {}
        for slider_name, slider_value in sliders.items():
            value_to_text = LEVELS.get(slider_name)
            sliders_text[slider_name] = value_to_text.get(slider_value)
        return sliders_text

    @staticmethod
    def _sliders_are_default(sliders) -> bool:
        """
        Check if parameters do not require any transformations
        :param sliders: transformation parameters
        :return: bool
        """
        default_state = {'politeness_level': 2, 'emotion_level': 1, 'humor_level': 0, 'extensiveness_level': 1}
        return sliders == default_state
