from app.db.repository.elastic_document_repository import ElasticsearchDocumentRepository
from app.db.repository.postgres_document_repository import PostgresDocumentRepository
from app.schemas.document import Document, DeleteDocumentResult, ElasticResult


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

    async def delete_document(self, doc_id : int) -> DeleteDocumentResult:
        es_rep_result = await self._es_rep.delete_document(doc_id)
        pg_rep_result = await self._pg_rep.delete_by_id(doc_id)


        return DeleteDocumentResult(
                elasticsearch_result= ElasticResult(
                index=es_rep_result.body.get("_index"),
                id=es_rep_result.body.get("_id"),
                result=es_rep_result.body.get("result")
            ),
            postgres_result=pg_rep_result
        )