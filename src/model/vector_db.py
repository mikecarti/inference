from typing import List

import numpy as np
from loguru import logger
from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings

from src.model.exceptions import InvalidAnswerException
from src.model.utils import wrap
from shutil import rmtree


class VectorDataBase:
    def __init__(self, embeddings=None):
        self.threshold = 0.6
        self.data_path = "data/chizhik.txt"
        self.db_path = "faiss_index"

        self.embeddings = self._init_embeddings(embeddings)
        self.db = self._specify_db()
        self._log_number_of_db_entries()

    async def amanual_search_with_weights(self, messages: List, k_nearest=4, verbose=True):
        messages_embeddings = [self.embeddings.embed_query(msg) for msg in messages]
        weights = [2 ** i for i in range(len(messages_embeddings))]
        normalized_weights = np.array(weights) / np.sum(weights)
        logger.debug(f"Weights: {normalized_weights}")
        expanded_weights = np.expand_dims(normalized_weights, axis=-1)

        weighted_embeddings = messages_embeddings * expanded_weights
        weighted_messages_sum = np.sum(weighted_embeddings, axis=0).tolist()

        similar_docs = await self.db.asimilarity_search_by_vector(weighted_messages_sum, k=k_nearest)

        similar_doc = similar_docs[0]
        if verbose:
            self._log_search(messages[-1], similar_doc)

        return similar_doc.page_content

    async def amanual_search(self, messages: List, verbose=True, k_nearest=4) -> str:
        query = ' '.join(messages)

        similar_docs = await self.db.asimilarity_search_with_relevance_scores(query, k=k_nearest)
        docs = [doc[0].page_content for doc in similar_docs]
        scores = [doc[1] for doc in similar_docs]

        best_doc = docs[0]
        best_doc_score = scores[0]
        aggregated_docs = "\n\n".join(docs)

        if verbose:
            self._log_search(messages[-1], best_doc, best_doc_score)
        if best_doc_score < self.threshold:
            return "Tell user that you can not help with that problem"
        else:
            return aggregated_docs

    @staticmethod
    def _log_search(query, similar_doc, score=None):
        if score:
            logger.debug(f"Score: {score}")
        logger.debug(f"Real Question: {wrap(str(query))}")
        logger.debug(f"Found Question: {similar_doc}")

    def _vectorize_docs(self, embeddings):
        """
        embeddings - usually OpenAIEmbeddings
        =========
        return - FAISS db
        """
        # грузим файл в лоадер
        loader = TextLoader(self.data_path)
        documents = loader.load()

        # создаем сплиттер документов, чтобы уложиться в лимит по токенам
        text_splitter = CharacterTextSplitter(separator="\n\n",
                                              chunk_size=0,
                                              chunk_overlap=0,
                                              length_function=len, )
        texts = text_splitter.split_documents(documents)

        # создаем хранилище
        db = FAISS.from_documents(texts, embeddings)
        db.as_retriever()

        return db

    def _save_db_locally(self, db):
        # сохранить хранилище локально
        rmtree(self.db_path, ignore_errors=False)
        db.save_local(self.db_path)

    def _load_vector_db(self):
        db = FAISS.load_local(self.db_path, self.embeddings)
        logger.info("Database loaded from local files")
        return db

    def _create_vector_db(self):
        logger.info("Creating vector database...")
        vector_db = self._vectorize_docs(self.embeddings)
        logger.info("Created vector database")
        return vector_db

    def _specify_db(self):
        logger.info("\n(1)Load vector db\n(2)Create one?\n\t [1/2]")
        ans = input()
        if ans == "1":
            vector_db = self._load_vector_db()
        elif ans == "2":
            vector_db = self._create_vector_db()
            self._save_db_locally(vector_db)
        else:
            raise InvalidAnswerException("Invalid answer")
        return vector_db

    @staticmethod
    def _init_embeddings(embeddings) -> OpenAIEmbeddings:
        if not embeddings:
            return OpenAIEmbeddings()
        else:
            return embeddings

    def _log_number_of_db_entries(self):
        number_of_entries = len(self.db.index_to_docstore_id)
        logger.debug(f"Number of entries in the VectorDB: {number_of_entries}")
