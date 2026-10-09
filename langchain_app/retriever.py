from langchain_community.vectorstores import FAISS

from config import VECTOR_DB_PATH
from langchain_app.embeddings import embeddings


def get_retriever():

    # The index is built locally by build_vector_db.py; FAISS stores
    # its docstore with pickle, so only load an index you created.
    vector_db = FAISS.load_local(
        str(VECTOR_DB_PATH),
        embeddings,
        allow_dangerous_deserialization=True,
    )

    return vector_db.as_retriever(
        search_type="similarity",
        search_kwargs={
            "k": 5,
        },
    )
