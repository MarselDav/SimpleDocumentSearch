from elasticsearch import AsyncElasticsearch

from app.schemas.document import Document


class ElasticsearchDocumentRepository:
    def __init__(self, client: AsyncElasticsearch):
        self._client = client

    async def create_document(self, document: Document):
        return await self._client.index(
            index='documents',
            id=str(document.id),
            document={
                "id": document.id,
                "text": document.text
            }
        )

    async def search(self, query: str, limit: int = 20):
        return await self._client.search(
            index='documents',
            query={
                "match": {
                    "text": query
                }
            },
            size=limit
        )

    async def delete_document(self, document_id):
        return await self._client.delete(
            index='documents',
            id=str(document_id)
        )
