import json
import re

manual_example = """Manual: Часть мануала для технической поддержки:  Проблема: У человека есть несколько учётных записей на один и тот же номер телефона.
Решение: 
Если пользователь дал номер телефона в своем сообщение напишите ему предложение состоящее лишь из его телефона.
Пример:
HelpDesk: +7 (985) 927-55-12
Если же пользователь не дал номер телефона, попросите его дать номер телефона

<{function_name: "check_autorized_accs", args: ["phone_number"] }>
"""


class ManualParser:
    def __init__(self):
        pass

    def parse_manual(self, manual_text: str):
        # Split the text based on parts inside "<...>" and outside of '<...>'
        parts = re.split(r'(<.*?>)', manual_text)
        # Remove empty parts and trim whitespace
        parts = [p.strip() for p in parts if p.strip()]

        manual_text = " ".join([p for p in parts if not p.startswith("<")])

        functions = [p for p in parts if p.startswith("<")]
        functions_plain_json = [self._remove_arrows(f) for f in functions]
        function_dicts = [json.loads(f) for f in functions_plain_json]

    def _remove_arrows(self, s: str):
        return s.replace("<", "").replace(">", "")
