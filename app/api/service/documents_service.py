from elasticsearch import NotFoundError
from fastapi import HTTPException
from sqlalchemy.exc import ProgrammingError

from app.db.repository.document_repository import DocumentRepository
from app.schemas.document import Document, DeleteDocumentResult


async def get_documents(query: str, doc_rep : DocumentRepository) \
        -> list[Document] | None:
    try:
        return await doc_rep.get_documents(query)
    except (ProgrammingError, NotFoundError) as exc:
        raise_errors(exc)


async def delete_document(doc_id: int, doc_rep : DocumentRepository) \
        -> DeleteDocumentResult | None:
    try:
        return await doc_rep.delete_document(doc_id)
    except (ProgrammingError, NotFoundError) as exc:
        raise_errors(exc)


def raise_errors(exc: Exception) -> None:
    if isinstance(exc, ProgrammingError):
        orig = exc.orig
        sqlstate = getattr(orig, "sqlstate", None)

        if sqlstate == "42P01":
            raise HTTPException(
                status_code=503,
                detail=(
                    "Таблица documents не существует. "
                    "Выполните миграции Alembic."
                ),
            ) from exc

    if isinstance(exc, NotFoundError):
        error = exc.body.get("error")

        if isinstance(error, dict):
            error_type = error.get("type", None)

            if error_type == "index_not_found_exception":
                raise HTTPException(
                    status_code=503,
                    detail=(
                        "Индекс documents не существует. "
                        "Проверьте наличие индекса documents и выполните импорт данных."
                    ),
                ) from exc

        if error is None:
            result = exc.body.get("result")

            if result == "not_found":
                raise HTTPException(
                    status_code=404,
                    detail=(
                        f"Необходимый документ с id={exc.body.get("_id")} не найден."
                    ),
                ) from exc

    raise exc
