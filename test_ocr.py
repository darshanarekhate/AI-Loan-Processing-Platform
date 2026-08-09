from database.document_repository import get_documents_by_application
from ocr.ocr_service import process_document

application_id = "APP-4FE3EF66"   # Replace with your application ID

documents = get_documents_by_application(application_id)

for doc in documents:

    if doc["document_type"] not in ["PAN", "AADHAAR"]:
        continue

    print("=" * 60)
    print(doc["document_type"])
    print(doc["file_path"])

    result = process_document(
        doc["document_type"],
        doc["file_path"]
    )

    print(result)