from langchain_community.vectorstores import FAISS

from langchain_app.embeddings import embeddings

VECTOR_DB_PATH = "faiss_index"


def get_retriever():

    vector_db = FAISS.load_local(
        VECTOR_DB_PATH,
        embeddings,
        allow_dangerous_deserialization=True,
    )

    return vector_db.as_retriever(
        search_type="similarity",
        search_kwargs={
            "k": 5,
        },
    )