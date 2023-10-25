class View:
    @staticmethod
    def process_answer(answer: str) -> str:
        """
        Beautify answer.
        :param answer:
        :return:
        """
        answer = answer.strip()
        answer = View.remove_prefixes(answer)
        return answer

    @classmethod
    def remove_prefixes(cls, answer: str) -> str:
        """
        There was a bug: AI prefix was present in model's output. It is the fix.
        :param answer:
        :return:
        """
        # костыль
        while answer.startswith("AI: "):
            answer = answer.replace("AI: ", "")
            answer = answer.strip()
        return answer
