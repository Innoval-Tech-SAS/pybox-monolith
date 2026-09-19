from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app_platform.documents.services.admin_document_service import AdminDocumentService
from app_platform.documents.services.document_service import DocumentService
from core.database.database import get_main_session


def get_document_service(
    db: Annotated[AsyncSession, Depends(get_main_session)],
) -> DocumentService:
    return DocumentService(db)


def get_admin_document_service(
    db: Annotated[AsyncSession, Depends(get_main_session)],
) -> AdminDocumentService:
    return AdminDocumentService(db)


DocumentServiceDep = Annotated[DocumentService, Depends(get_document_service)]
AdminDocumentServiceDep = Annotated[AdminDocumentService, Depends(get_admin_document_service)]
