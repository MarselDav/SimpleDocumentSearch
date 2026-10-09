from app.db.repository.document_repository import DocumentRepository
from fastapi import Request


def get_doc_rep(request: Request) -> DocumentRepository:
    return request.app.state.doc_rep
