from fastapi import APIRouter
from app.api.service import documents_service

router = APIRouter()

@router.get("/documents/")
async def get_documents():
    return await documents_service.get_documents()