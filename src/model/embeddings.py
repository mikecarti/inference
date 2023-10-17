from typing import Dict, List

import numpy as np
from langchain.embeddings.huggingface import HuggingFaceInferenceAPIEmbeddings
from loguru import logger
import requests
import time


def _custom_embed_query_func(self, text: str) -> List[float]:
    """Compute query embeddings using a HuggingFace transformer model.

    Args:
        text: The text to embed.

    Returns:
        Embeddings for the text.
    """
    emb = self.embed_documents([text])
    logger.debug(f"Shape of embedding: {np.array(emb).shape}\nResponse trunc.: {emb[0][:3]}")
    # make embeddings compatible
    embeddings = emb[0]

    logger.debug(f"New Shape of embedding: {np.array(embeddings).shape}\nNew Response trunc.: {embeddings[:3]}")
    return embeddings


class CustomEmbeddings():
    API_URL = "https://api-inference.huggingface.co/models/intfloat/multilingual-e5-large"
    headers = {"Authorization": "Bearer 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"}
    ERROR_COLD_START = "Model intfloat/multilingual-e5-large is currently loading"

    def __init__(self):
        # change function for our custom function
        # HuggingFaceInferenceAPIEmbeddings.embed_query = _custom_embed_query_func
        api_key = self.headers.get("Authorization").split(" ")[1]

        self.embeddings = HuggingFaceInferenceAPIEmbeddings(
            api_key=api_key,
            model_name="intfloat/multilingual-e5-large"
        )
        self._test_query("Test Test")

    def _test_query(self, payload):
        # Returns error with estimated time if model is still loading
        response = requests.post(self.API_URL, headers=self.headers, json=payload).json()

        while self._model_is_loading(response):
            extra_time_just_in_case = 1.0
            time.sleep(response["estimated_time"] + extra_time_just_in_case)
            response = requests.post(self.API_URL, headers=self.headers, json=payload).json()

            logger.debug(f"Shape of embedding: {np.array(response).shape}Response: {response[:3]}")
        return response

    def _model_is_loading(self, response: Dict):
        if isinstance(response, list):
            return False

        return response["error"] and response["error"] == self.ERROR_COLD_START

    def get(self):
        return self.embeddings
