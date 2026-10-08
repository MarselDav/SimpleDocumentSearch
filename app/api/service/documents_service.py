from app.models.document import Document
from datetime import datetime

async def get_documents() -> Document:
    return Document(
        id=1,
        text="Example text",
        rubrics=["r1", "r2", "r3"],
        created_date=datetime.now(),
    )