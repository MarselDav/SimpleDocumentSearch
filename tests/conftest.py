from typing import AsyncGenerator

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx2 import ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sympy import refine

from app.api.deps import get_doc_rep
from app.api.main import app
from elasticsearch import AsyncElasticsearch
from dotenv import load_dotenv
import os
from httpx import ASGITransport, AsyncClient

from sqlalchemy import insert, delete
from app.db.models.document import DocumentORM

from app.db.repository.document_repository import DocumentRepository
from app.db.repository.elastic_document_repository import ElasticsearchDocumentRepository
from app.db.repository.postgres_document_repository import PostgresDocumentRepository

from elasticsearch.helpers import async_bulk

load_dotenv()

ELASTICSEARCH_URL = os.environ["ELASTICSEARCH_URL"]
ELASTICSEARCH_USERNAME = os.environ["ELASTICSEARCH_USERNAME"]
ELASTIC_PASSWORD = os.environ["ELASTIC_PASSWORD"]
INDEX_NAME = "test_document"

@pytest_asyncio.fixture
async def test_es_client() \
        -> AsyncGenerator[AsyncElasticsearch, None]:

    async with AsyncElasticsearch(
        ELASTICSEARCH_URL,
        basic_auth=(
                ELASTICSEARCH_USERNAME,
                ELASTIC_PASSWORD
        )
    ) as client:

        if await client.indices.exists(index=INDEX_NAME):
            await client.indices.delete(index=INDEX_NAME)


        await client.indices.create(
            index=INDEX_NAME,
            mappings={
                "properties": {
                    "id": {"type": "long"},
                    "text": {"type": "text"},
                }
            }
        )

        try:
            yield client
        finally:
            if await client.indices.exists(index=INDEX_NAME):
                await client.indices.delete(index=INDEX_NAME)

@pytest_asyncio.fixture
async def test_pg_session_factory():
    user = os.environ["POSTGRES_USER"]
    password = os.environ["POSTGRES_PASSWORD"]
    host = os.environ["POSTGRES_HOST"]
    port = os.environ["POSTGRES_PORT"]
    # dbname = "test_document"

    test_database_url = f"postgresql+asyncpg://{user}:{password}@{host}:{port}/test_document"

    test_engine = create_async_engine(
        test_database_url,
        echo=True,
    )

    test_async_session_factory = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    # удаление всех записей в тестовой БД
    async with test_async_session_factory() as session:
        await session.execute(delete(DocumentORM))
        await session.commit()

    try:
        yield test_async_session_factory
    finally:
        await test_engine.dispose()

@pytest.fixture
def test_get_doc_rep(test_es_client, test_pg_session_factory):
    pg_rep = PostgresDocumentRepository(test_pg_session_factory)
    es_rep = ElasticsearchDocumentRepository(test_es_client, INDEX_NAME)

    return DocumentRepository(pg_rep, es_rep)

@pytest_asyncio.fixture
async def test_client(test_get_doc_rep):
    app.dependency_overrides[get_doc_rep] = lambda: test_get_doc_rep

    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport,
                               base_url="http://test") as client:
            yield client
    finally:
        app.dependency_overrides.pop(get_doc_rep, None)

@pytest_asyncio.fixture
async def seed_documents(test_es_client, test_pg_session_factory):
    async def _seed(documents_data : list[dict]):
        async with test_pg_session_factory() as session:
            if documents_data:
                # await session.execute(delete(DocumentORM))

                await session.execute(
                    insert(DocumentORM),
                    documents_data
                )
                await session.commit()

        if documents_data:
            records = [
                {"_index": INDEX_NAME,
                 "_id": str(document["id"]),
                 "_source": {"id": document["id"], "text": document["text"]}
                 } for document in documents_data]

            await async_bulk(
                client=test_es_client,
                actions=records,
                raise_on_error=False
            )

            await test_es_client.indices.refresh(index=INDEX_NAME)
        return documents_data
    return _seed