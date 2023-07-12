from langchain.document_loaders import DataFrameLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
import pandas as pd
from utils import wrap
from shutil import rmtree


class VectorDataBase:
    def __init__(self, embeddings=None):
        self.data_path = "data/data.csv"
        self.db_path = "faiss_index"

        self.embeddings = self._init_embedddings(embeddings)
        self.db = self._specify_db()

    async def asimilarity_search(self, query):
        similar_docs = await self.db.asimilarity_search(query)
        similar_doc = similar_docs[0]
        return similar_doc

    async def amanual_search(self, query, verbose=True):
        doc = await self.asimilarity_search(query)
        manual = doc.metadata['answer']
        similar_question = doc.page_content

        if verbose:
            print(f"\tReal Question: {wrap(query)} \n\n\tFound Question: {wrap(similar_question)} \
        \n\n\tManual: {wrap(manual)}")

        return manual

    def _vectorize_docs(self, df: pd.DataFrame, embeddings):
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

        # сохранить хранилище локально
        rmtree(self.db_path, ignore_errors=False)
        db.save_local(self.db_path)
        return db

    def _create_vector_db(self):
        print("Creating vector database...")
        ru_encoding = 'cp1251'
        df = pd.read_csv(self.data_path, sep=';', encoding=ru_encoding)
        df.columns = ['id', 'question', 'answer']
        vector_db = self._vectorize_docs(df, self.embeddings)
        print("Created vector database")
        return vector_db

    def _load_vector_db(self):
        return FAISS.load_local(self.db_path, self.embeddings)

    def _specify_db(self):
        print("(1)Load vector db\n(2)Create one?\n\t [1/2]")
        ans = input()
        if ans == "1":
            vector_db = self._load_vector_db()
        elif ans == "2":
            vector_db = self._create_vector_db()
        else:
            raise Exception("Invalid answer")
        return vector_db

    def _init_embedddings(self, embeddings):
        if not embeddings:
            return OpenAIEmbeddings()
        else:
            return embeddings

