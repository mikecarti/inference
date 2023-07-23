import json
import re
from dataclasses import dataclass
from typing import List, Union, Dict

manual_example = """Manual: Часть мануала для технической поддержки:  Проблема: У человека есть несколько учётных записей на один и тот же номер телефона.
Решение: 
Если пользователь дал номер телефона в своем сообщение напишите ему предложение состоящее лишь из его телефона...

Игнорируй содержимое этих кавычек: <{function_name: "check_autorized_accs", kwargs: ["phone_number"] }>
"""


@dataclass
class FunctionPrototype:
    function_name: str
    kwargs: Dict


class ManualParser:
    def __init__(self):
        self.regexp_functions = r'(<.*?>)'

    def process_manual(self, manual_text: str) -> (str, Union[List[FunctionPrototype], None]):
        if self._manual_has_functions(manual_text):
            manual_part, functions = self._parse_manual(manual_text)
            return manual_part, functions
        else:
            return manual_text, None

    def _parse_manual(self, manual_text: str) -> (str, List[FunctionPrototype]):
        """
        Parses manual into manual_part and functions that has to be called
        :param manual_text: string
        :return: First value is a manual_part
        :return: Second value is a functions list with dictionaries containing function_name and kwargs dictionary
        Example: [...,{"function_name": "func", "kwargs": {"x", "y"}} , ..., ...]
        """
        # Split the text based on parts inside "<...>" and outside of '<...>'
        parts = re.split(self.regexp_functions, manual_text)
        # Remove empty parts and trim whitespace
        parts = [p.strip() for p in parts if p.strip()]

        manual_text = " ".join([p for p in parts if not p.startswith("<")])

        functions_plain_text = [p for p in parts if p.startswith("<")]
        functions_plain_json = [self._remove_arrows(f) for f in functions_plain_text]
        function_dicts = [json.loads(f) for f in functions_plain_json]
        functions = [FunctionPrototype(function_name=func["function_name"], kwargs=func["kwargs"]) for func in
                     function_dicts]

        return manual_text, functions

    def _remove_arrows(self, s: str):
        return s.replace("<", "").replace(">", "")

    def _manual_has_functions(self, manual_text: str):
        if re.match(self.regexp_functions, manual_text):
            return True
        else:
            return False

