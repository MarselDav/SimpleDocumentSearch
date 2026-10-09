from fastapi import APIRouter
from app.api.service import documents_service
from fastapi import Depends
from typing import Annotated
from app.db.database import get_session, AsyncSession
from app.api.deps import get_doc_rep
from app.db.repository.document_repository import DocumentRepository
from app.db.repository.postgres_document_repository import PostgresDocumentRepository

router = APIRouter()

DocumentRepositoryDep = Annotated[DocumentRepository, Depends(get_doc_rep)]

@router.get("/get_documents/")
async def get_documents(query : str, doc_rep : DocumentRepositoryDep):
    """
    Принимает на вход произвольный текстовый запрос,
     ищет по тексту документа в Индексе и возвращает первые 20 документов
      со всем полями БД, упорядоченные по дате создания.
    """
    return await documents_service.get_documents(query, doc_rep)


@router.delete("/delete_document/{doc_id}")
async def delete_document(doc_id : int, doc_rep : DocumentRepositoryDep):
    """
    Удаляет документ из БД и Индекса по полю id.
    """
    return await documents_service.delete_document(doc_id, doc_rep)