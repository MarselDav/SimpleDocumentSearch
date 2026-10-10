from contextlib import contextmanager, asynccontextmanager

from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from app.api.router.documents import router as documents_router
from app.db.database import AsyncSessionFactory, engine
from app.db.repository.postgres_document_repository import PostgresDocumentRepository
from app.db.repository.elastic_document_repository import ElasticsearchDocumentRepository
from app.db.repository.document_repository import DocumentRepository
import os
from dotenv import load_dotenv

load_dotenv()

ELASTICSEARCH_URL = os.environ["ELASTICSEARCH_URL"]
ELASTICSEARCH_USERNAME = os.environ["ELASTICSEARCH_USERNAME"]
ELASTIC_PASSWORD = os.environ["ELASTIC_PASSWORD"]


@asynccontextmanager
async def lifespan(app: FastAPI):
    client = AsyncElasticsearch(
            ELASTICSEARCH_URL,
            basic_auth=(
                    ELASTICSEARCH_USERNAME,
                    ELASTIC_PASSWORD)
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