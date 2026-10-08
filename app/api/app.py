from app.api.router.documents import router as documents_router
from fastapi import FastAPI


app = FastAPI(
    title="SimpleDocumentsSearch",
)

app.include_router(documents_router, tags=["documents"])