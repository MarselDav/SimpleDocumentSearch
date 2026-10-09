from app.db.repository.document_repository import DocumentRepository

async def get_documents(query: str, doc_rep : DocumentRepository):
    return await doc_rep.get_documents(query)


async def delete_document(doc_id: int, doc_rep : DocumentRepository):
    return await doc_rep.delete_document(doc_id)