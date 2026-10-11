from contextlib import asynccontextmanager

from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from app.api.router.documents import router as documents_router
from app.db.database import AsyncSessionFactory, engine
from app.db.repository.postgres_document_repository import PostgresDocumentRepository
from app.db.repository.elastic_document_repository import ElasticsearchDocumentRepository
from app.db.repository.document_repository import DocumentRepository
from app.config.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    client = AsyncElasticsearch(
            settings.elasticsearch_url,
            basic_auth=(
                    settings.elasticsearch_username,
                    settings.elastic_password.get_secret_value())
    )

    print("[ELASTIC SEARCH PING]", await client.ping())

    try:
        pg_rep = PostgresDocumentRepository(AsyncSessionFactory)
        es_rep = ElasticsearchDocumentRepository(client)
        app.state.doc_rep = DocumentRepository(pg_rep, es_rep)
        yield
    finally:
        await client.close()
        await engine.dispose()


app = FastAPI(
    title="SimpleDocumentsSearch",
    lifespan=lifespan,
)

app.include_router(documents_router, tags=["documents"])