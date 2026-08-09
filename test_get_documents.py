from database.document_repository import get_documents_by_application

documents = get_documents_by_application("APP-17ED0216")

for doc in documents:
    print(dict(doc))