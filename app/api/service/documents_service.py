from app.schemas.document import Document
from datetime import datetime
from app.db.database import AsyncSession
from app.db.models.document import DocumentORM
from sqlalchemy import select


async def get_documents(id: int, session: AsyncSession):
    result = await session.execute(
        select(DocumentORM)
        .where(DocumentORM.id == id)
    )

    return result.scalar_one_or_none()
