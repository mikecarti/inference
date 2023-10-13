import time
from typing import List, Dict

import requests
from loguru import logger

from langchain.embeddings.base import Embeddings

class CustomEmbeddings(Embeddings):
    API_URL = "https://api-inference.huggingface.co/models/intfloat/multilingual-e5-large"
    headers = {"Authorization": "Bearer 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"}
    ERROR_COLD_START = "Model intfloat/multilingual-e5-large is currently loading"

    def __init__(self):
        logger.debug(f"Test embedding initialization...")
        response = self.embed_query("we are testing")
        logger.debug(f"Response: {response}")

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
        if isinstance(response, list):
            return False
        return response["error"] and response["error"] == self.ERROR_COLD_START

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        embeddings = [self.embed_query(t) for t in texts]
        return embeddings

    def embed_query(self, text: str) -> List[float]:
        """Embed query text."""
        embedding = self._query(text)

        err_msg = f"Error, wrong type: {embedding} \n Type: {type(embedding)}"
        assert isinstance(embedding, list), err_msg
        assert isinstance(embedding[0], float), err_msg

        return embedding
