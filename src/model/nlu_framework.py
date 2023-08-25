import os
from enum import Enum

from src.model.exceptions import UnknownIntentException


class Intents(Enum):
    FALLBACK = "Default Fallback Intent"
    DELIVERY_STATUS = "Delivery Status Intent"
    CASHBACK_BALANCE = "Cashback Balance Intent"


class NLUFramework:
    credentials_path = 'data/credentials.json'
    project_id = 'helpdeskagent-vlbw'
    language_code = 'ru'

    def __init__(self):
        pass
    # self.session_client = dialogflow.SessionsClient.from_service_account_json(self.credentials_path)

    def run(self, query) -> str | None:
        return None
        intent = self.detect_intent(query)
        result = self.process_intent(intent)
        return result

    def detect_intent(self, text: str) -> dict:
        session_id = 'unique-session-id'
        session = self.session_client.session_path(self.project_id, session_id)

        text_input = dialogflow.TextInput({"text": text, "language_code": self.language_code})
        query_input = dialogflow.QueryInput({"text": text_input})

        response = self.session_client.detect_intent(
            session=session,
            query_input=query_input
        )

        intent_display_name = response.query_result.intent.display_name
        return intent_display_name

    def process_intent(self, intent: str) -> str | None:
        intent = intent.strip()
        if intent == Intents.DELIVERY_STATUS.value:
            return "Ваш статус посылки - Тест"
        elif intent == Intents.CASHBACK_BALANCE.value:
            return "Кэшбек баланс - Тест"
        elif intent == Intents.FALLBACK.value:
            return None
        else:
            raise UnknownIntentException(f"Unknown intent: {intent}")
