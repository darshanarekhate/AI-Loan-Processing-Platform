from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from config import KNOWLEDGE_BASE_PATH, VECTOR_DB_PATH
from langchain_app.embeddings import embeddings


def build_vector_store():

    documents = []

    # sorted() keeps the index build reproducible across platforms.
    for path in sorted(KNOWLEDGE_BASE_PATH.glob("*.txt")):

        loader = TextLoader(
            str(path),
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

    vector_db.save_local(str(VECTOR_DB_PATH))

    return vector_db