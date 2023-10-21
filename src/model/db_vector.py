import threading
from typing import List

from loguru import logger
from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings.base import Embeddings

from langchain.embeddings import HuggingFaceEmbeddings
from src.model.utils import wrap
from shutil import rmtree


class VectorDataBase:
    # change for "intfloat/multilingual-e5-large" if you have enough RAM
    EMBEDDING_HF_NAME = "intfloat/multilingual-e5-small"
    THRESHOLD: float = 0.6
    CONSOLE_WAIT_DEFAULT: int = 3
    CREATE_NEW_VECTOR_DB: bool = True

    def __init__(self, embeddings=None):
        self.data_path = "data/about_us.txt"
        self.db_path = "faiss_index"

        self.embeddings = self._init_embeddings(embeddings)
        self.db = self._specify_db()
        self._log_number_of_db_entries()

    async def amanual_search(self, messages: List, verbose=True, k_nearest=4) -> str:
        """
        Search concatenation of last messages to find k most similar documents.
        :param messages:
        :param verbose:
        :param k_nearest:
        :return:
        """
        query = ' '.join(messages)

        similar_docs = await self.db.asimilarity_search_with_relevance_scores(query, k=k_nearest)
        docs = [doc[0].page_content for doc in similar_docs]
        scores = [doc[1] for doc in similar_docs]

        best_doc = docs[0]
        best_doc_score = scores[0]
        aggregated_docs = "\n\n".join(docs)

        if verbose:
            self._log_search(messages[-1], best_doc, best_doc_score)
        if best_doc_score < self.THRESHOLD:
            return "Tell user that you can not help with that problem"
        else:
            return aggregated_docs

    @staticmethod
    def _log_search(query, similar_doc, score=None) -> None:
        """
        Log search results
        :param query:
        :param similar_doc:
        :param score:
        :return:
        """
        if score:
            logger.debug(f"Score: {score}")
        logger.debug(f"Real Question: {wrap(str(query))}")
        logger.debug(f"Found Question: {similar_doc}")

    def _vectorize_docs(self) -> FAISS:
        """
        Create vector database from files.
        :return:
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
        db = FAISS.from_documents(texts, self.embeddings)
        db.as_retriever()

        return db

    def _save_db_locally(self, db) -> None:
        """
        Save a Database to file
        :param db:
        :return:
        """
        # delete previous db
        rmtree(self.db_path, ignore_errors=True)
        # save new db locally
        db.save_local(self.db_path)

    def _load_vector_db(self) -> FAISS:
        """
        Loads saved db from file
        :return:
        """
        db = FAISS.load_local(self.db_path, self.embeddings)
        logger.info("Database loaded from local files")
        return db

    def _create_vector_db(self) -> FAISS:
        """
        :return:
        """
        logger.info("Creating vector database...")
        vector_db = self._vectorize_docs()
        logger.info("Created vector database")
        return vector_db

    def _specify_db(self) -> FAISS:
        """
        May be hardcoded to either create new db, or to load existing
        :return: 
        """
        load_existing = not self.CREATE_NEW_VECTOR_DB

        if load_existing:
            return self._load_vector_db()
        else:
            vector_db = self._create_vector_db()
            self._save_db_locally(vector_db)
        return vector_db

    def _init_embeddings(self, embeddings) -> Embeddings:
        """
        Init chosen in class creation embeddings, if none are chosen, init default.
        :param embeddings: 
        :return: 
        """
        if embeddings:
            return embeddings
        default_embeddings = HuggingFaceEmbeddings(model_name=self.EMBEDDING_HF_NAME)
        return default_embeddings

    def _log_number_of_db_entries(self):
        """
        Log number of database vectorized documents
        :return: 
        """
        number_of_entries = len(self.db.index_to_docstore_id)
        logger.debug(f"Number of entries in the VectorDB: {number_of_entries}")
