from typing import Dict

from langchain.embeddings.huggingface import HuggingFaceInferenceAPIEmbeddings
from loguru import logger
import requests
import time


class CustomEmbeddings():
    API_URL = "https://api-inference.huggingface.co/models/intfloat/multilingual-e5-large"
    headers = {"Authorization": "Bearer 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"}
    ERROR_COLD_START = "Model intfloat/multilingual-e5-large is currently loading"

    def __init__(self):
        self.embeddings = HuggingFaceInferenceAPIEmbeddings(
            api_key=self.API_URL,
            model_name="intfloat/multilingual-e5-large"
        )

        self._query()

        query_result = self.embeddings.embed_query(" Privet, Prive,t Privet")
        logger.debug(f"Test embeddings: {query_result}")

    def _query(self, payload):
        # Returns error with estimated time if model is still loading
        response = requests.post(self.API_URL, headers=self.headers, json=payload).json()

        while self._model_is_loading(response):
            extra_time_just_in_case = 1.0
            time.sleep(response["estimated_time"] + extra_time_just_in_case)
            response = requests.post(self.API_URL, headers=self.headers, json=payload).json()

            logger.debug("Response: ", response)
        return response

    def _model_is_loading(self, response: Dict):
        return response["error"] and response["error"] == self.ERROR_COLD_START


    def get(self):
        return self.embeddings
