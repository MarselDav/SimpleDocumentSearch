from sqlalchemy.exc import IntegrityError

from app.db.models.document import DocumentORM
from sqlalchemy import select, delete, insert

from app.schemas.document import Document


class PostgresDocumentRepository:
    def __init__(self, session_factory):
        self._session_factory = session_factory

    async def get_by_id(self, document_id: int) -> Document | None:
        async with self._session_factory() as session:
            result = await session.execute(
                select(DocumentORM)
                .where(DocumentORM.id == document_id)
            )

            document_orm = result.scalar()
            if document_orm:
                return Document.model_validate(document_orm)

            return None

    async def get_by_ids(self, doc_ids: list[int]) -> list[Document]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(DocumentORM)
                .where(DocumentORM.id.in_(doc_ids))
                .order_by(DocumentORM.created_date)
            )

            return [Document.model_validate(row) for row in result.scalars().all()]

    async def insert(self, document: Document) -> DocumentORM | None:
        try:
            async with (self._session_factory() as session):
                result = await session.execute(
                    insert(DocumentORM)
                    .values(**document.model_dump())
                    .returning(DocumentORM)
                )
                await session.commit()

                return result.scalar_one_or_none()

        except IntegrityError:
            return None

    async def delete_by_id(self, document_id: int) -> bool:
        async with (self._session_factory() as session):
            result = await session.execute(
                delete(DocumentORM)
                .where(DocumentORM.id == document_id)
            )
            await session.commit()

            return result.rowcount > 0