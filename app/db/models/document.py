from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ARRAY, String, Text, DateTime, Integer
from datetime import datetime
from .base import Base

class DocumentORM(Base):
    __tablename__ = "document"

    id : Mapped[int] = mapped_column(
        primary_key=True,
    )

    text : Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    created_date : Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False
    )

    rubrics : Mapped[list[str]] = mapped_column(
        ARRAY(String),
        nullable = False
    )