from app.db.models.document import DocumentORM
from app.db.repository.elastic_document_repository import ElasticsearchDocumentRepository
from app.db.repository.postgres_document_repository import PostgresDocumentRepository
from app.schemas.document import Document


class DocumentRepository:
    def __init__(self,
                 pg_rep: PostgresDocumentRepository,
                 es_rep: ElasticsearchDocumentRepository):
        self._pg_rep = pg_rep
        self._es_rep = es_rep

    async def get_documents(self, query: str) -> list[Document]:
        result = await self._es_rep.search(query)
        doc_ids = [hit["_source"]["id"] for hit in result['hits']['hits']]

        return await self._pg_rep.get_by_ids(doc_ids)

    async def delete_document(self, doc_id : int) -> dict:
        es_rep_result = await self._es_rep.delete_document(doc_id)
        pg_rep_result = await self._pg_rep.delete_by_id(doc_id)

        return {
            "_es_rep" : es_rep_result,
            "_pg_rep": pg_rep_result,
        }