import os

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_app.embeddings import embeddings


KNOWLEDGE_PATH = "knowledge_base"


def build_vector_store():

    documents = []

    for filename in os.listdir(KNOWLEDGE_PATH):

        if filename.endswith(".txt"):

            loader = TextLoader(
                os.path.join(KNOWLEDGE_PATH, filename),
                encoding="utf-8",
            )

            documents.extend(loader.load())

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
    )

    chunks = splitter.split_documents(documents)

    print(f"Total documents: {len(documents)}")
    print(f"Total chunks: {len(chunks)}")

    vector_db = FAISS.from_documents(
        chunks,
        embeddings,
    )

    vector_db.save_local("faiss_index")

    return vector_db