class View:
    @staticmethod
    def process_answer(answer):
        answer = answer.strip()
        answer = View.remove_prefixes(answer)
        return answer

    @classmethod
    def remove_prefixes(cls, answer):
        if answer.startswith("AI: "):
            return answer.replace("AI: ", "")
        return answer
