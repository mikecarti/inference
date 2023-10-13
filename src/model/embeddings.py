import asyncio
from typing import List, Dict

from langchain.embeddings.base import Embeddings
import requests
from loguru import logger


class CustomEmbeddings(Embeddings):
    API_URL = "https://api-inference.huggingface.co/models/intfloat/multilingual-e5-large"
    headers = {"Authorization": "Bearer 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"}
    ERROR_COLD_START = "Model intfloat/multilingual-e5-large is currently loading"

    def __init__(self):
        logger.debug(f"Test embedding initialization...")
        response = self.embed_query("we are testing")
        logger.debug(f"Response: {response}")

    async def _aquery(self, payload):
        response = requests.post(self.API_URL, headers=self.headers, json=payload).json()

        while self._model_is_loading(response):
            await asyncio.sleep(response["estimated_time"])
            response = requests.post(self.API_URL, headers=self.headers, json=payload).json()
            print("Response: ", response)
        return response

    def _model_is_loading(self, response: Dict):
        if isinstance(response, list):
            return False
        return response["error"] and response["error"] == self.ERROR_COLD_START

    async def aembed_documents(self, texts: List[str]) -> List[List[float]]:
        embeddings = []
        for t in texts:
            embeddings.append(await self.aembed_query(t))
        return embeddings

    async def aembed_query(self, text: str) -> List[float]:
        """Embed query text."""
        embedding = self._aquery(text)

        err_msg = f"Error, wrong type: {embedding} \n Type: {type(embedding)}"
        assert isinstance(embedding, list), err_msg
        assert isinstance(embedding[0], float), err_msg

        return embedding


