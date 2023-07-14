class View:
    @staticmethod
    def process_answer(answer):
        answer = answer.strip()
        answer = View.remove_prefixes(answer)
        return answer

    @classmethod
    def remove_prefixes(cls, answer):
        # костыль
        while answer.startswith("AI: "):
            answer = answer.replace("AI: ", "")
            answer = answer.strip()
        return answer
