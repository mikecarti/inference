import codecs
from typing import List

import chardet as chardet
import numpy as np
from loguru import logger
from langchain.document_loaders import DataFrameLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
import pandas as pd

from src.model.exceptions import InvalidAnswerException
from src.model.utils import wrap
from shutil import rmtree


class VectorDataBase:
    def __init__(self, embeddings=None):
        self.threshold = 0.6
        self.data_path = "data/data.csv"
        self.db_path = "faiss_index"

        self.embeddings = self._init_embeddings(embeddings)
        self.db = self._specify_db()

    async def amanual_search_with_weights(self, messages: List, k_nearest=4, verbose=True):
        messages_embeddings = [self.embeddings.embed_query(msg) for msg in messages]
        weights = [2 ** i for i in range(len(messages_embeddings))]
        logger.debug(f"Weights: {weights}")
        normalized_weights = np.array(weights) / np.sum(weights)
        expanded_weights = np.expand_dims(normalized_weights, axis=-1)

        weighted_embeddings = messages_embeddings * expanded_weights
        weighted_messages_sum = np.sum(weighted_embeddings, axis=0).tolist()

        similar_docs = await self.db.asimilarity_search_by_vector(weighted_messages_sum, k=k_nearest)

        similar_doc = similar_docs[0]
        if verbose:
            self._log_search(messages[-1], similar_doc)

        return similar_doc.metadata['answer']

    async def amanual_search(self, messages: List, verbose=True, k_nearest=4) -> (str, str):
        query = ' '.join(messages)

        similar_docs = await self.db.asimilarity_search_with_relevance_scores(query, k=k_nearest)
        similar_doc = similar_docs[0][0]
        score = similar_docs[0][1]
        if verbose:
            self._log_search(messages[-1], similar_doc, score)

        if score < self.threshold:
            return "Tell user that you can not help with that problem"
        else:
            return similar_doc.metadata['answer']

    def _log_search(self, query, similar_doc, score=None):
        if score:
            logger.debug(f"Score: {score}")
        logger.debug(f"Real Question: {wrap(str(query))}")
        logger.debug(f"Found Question: {similar_doc.page_content}")


    @staticmethod
    def _vectorize_docs(df: pd.DataFrame, embeddings):
        """
        df - DataFrame that has 'question' column
        embeddings - usually OpenAIEmbeddings
        =========
        return - FAISS db
        """
        # грузим фрейм в лоадер, выделив колонку для векторизации (здесь может быть место для дискуссий)
        loader = DataFrameLoader(df, page_content_column='question')
        documents = loader.load()

        # создаем сплиттер документов, чтобы уложиться в лимит по токенам, в нашем случае это не очень полезный шаг
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
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
        df = self._read_data_for_db()
        vector_db = self._vectorize_docs(df, self.embeddings)
        logger.info("Created vector database")
        return vector_db

    def _update_vector_db(self):
        logger.info("Updating vector database...")
        old_db = FAISS.load_local(self.db_path, self.embeddings)
        new_data = self._read_data_for_db()
        new_db = self._vectorize_docs(new_data, embeddings=self.embeddings)
        old_db.merge_from(new_db)
        logger.info("Updated vector database")
        return old_db

    def _read_data_for_db(self):
        encoding = "utf-8"
        # self._set_encoding_of_data_file(encoding)

        df = pd.read_csv(self.data_path, sep=';', encoding=encoding)
        df.columns = ['id', 'question', 'answer']
        return df

    def _specify_db(self):
        logger.info("\n(1)Load vector db\n(2)Create one?\n(3)Update with new data\n\t [1/2/3]")
        ans = input()
        if ans == "1":
            vector_db = self._load_vector_db()
        elif ans == "2":
            vector_db = self._create_vector_db()
            self._save_db_locally(vector_db)
        elif ans == "3":
            vector_db = self._update_vector_db()
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
