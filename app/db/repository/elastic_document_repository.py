from elasticsearch import AsyncElasticsearch

from app.schemas.document import Document


class ElasticsearchDocumentRepository:
    def __init__(self, client: AsyncElasticsearch, index_name="documents"):
        self._client = client
        self._index_name = index_name

    async def create_document(self, document: Document):
        return await self._client.index(
            index=self._index_name,
            id=str(document.id),
            document={
                "id": document.id,
                "text": document.text
            }
        )

    async def search(self, query: str, limit: int = 20):
        return await self._client.search(
            index=self._index_name,
            query={
                "match": {
                    "text": query
                }
            },
            size=limit
        )

    async def delete_document(self, document_id):
        return await self._client.delete(
            index=self._index_name,
            id=str(document_id)
        )
