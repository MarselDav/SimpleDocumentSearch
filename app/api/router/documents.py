from fastapi import APIRouter
from app.api.service import documents_service
from fastapi import Depends
from typing import Annotated
from app.db.database import get_session, AsyncSession

router = APIRouter()

SessionDep = Annotated[AsyncSession, Depends(get_session)]

@router.get("/get_documents/{id}")
async def get_documents(id : int, session : SessionDep):
    """
    Принимает на вход произвольный текстовый запрос,
     ищет по тексту документа в Индексе и возвращает первые 20 документов
      со всем полями БД, упорядоченные по дате создания.
    """
    return await documents_service.get_documents(id, session)


@router.delete("/delete_document/{id}")
async def get_documents(id : int):
    """
    Удаляет документ из БД и Индекса по полю id.
    """
    return id