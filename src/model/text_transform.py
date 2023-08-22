from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.schema import SystemMessage
from loguru import logger


class TextTransformer:
    def __init__(self):
        self._llm = ChatOpenAI(model="gpt-3.5-turbo")

    def transform_text(self, text: str, anger: int, misspelling: int) -> str:
        prompt = self._build_transformation_prompt(question=text, anger=anger, misspelling=misspelling)
        return self._llm(prompt).content

    def _build_transformation_prompt(self, question: str, anger: int, misspelling: int) -> list:
        anger_text, misspelling_text = self._convert_sliders_to_text(anger=anger, misspelling=misspelling)
        prompt = PROMPT.format_messages(question=question, anger_level=anger_text, misspelling_level=misspelling_text)
        logger.debug(f"Prompt after formatting: {prompt[1].content}")
        return prompt

    @staticmethod
    def _convert_sliders_to_text(anger: int, misspelling: int) -> tuple[str, str]:
        anger_text = ANGER_LEVELS.get(anger)
        misspelling_text = MISSPELLING_LEVELS.get(misspelling)

        return anger_text, misspelling_text


PROMPT = ChatPromptTemplate.from_messages(
    [
        SystemMessage(
            content="Forget all previous instructions. You help change questions according to rules. "
                    "Dont be afraid to be "
                    "rude or "
                    "grammatically incorrect"
        ),
        HumanMessagePromptTemplate.from_template("Change this question so it would satisfy all these points \n"
                                                 " 0) the question is written in russian\n"
                                                 " 1) the question is {anger_level}\n"
                                                 " 2) the question is {misspelling_level}\n"
                                                 " Make sure modified question satisfies every point\n"
                                                 "Original Question: {question} \nModified Question:"),
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
