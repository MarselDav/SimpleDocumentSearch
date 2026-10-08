from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import ARRAY, String
from datetime import datetime

class Base(DeclarativeBase):
    pass

class DocumentORM(Base):
    __tablename__ = "document"

    id : Mapped[int] = mapped_column(
        primary_key=True
    )
    text : Mapped[str]
    rubrics : Mapped[list[str]] = mapped_column(
        ARRAY(String)
    )
    created_time : Mapped[datetime]
