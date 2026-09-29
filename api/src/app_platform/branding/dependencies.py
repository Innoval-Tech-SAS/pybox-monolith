from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app_platform.branding.repository.platform_branding_repository import (
    PlatformBrandingRepository,
)
from app_platform.branding.services.platform_branding_service import (
    PlatformBrandingService,
)
from app_platform.documents.services.document_service import DocumentService
from core.database.database import get_main_session


def get_platform_branding_service(
    db: Annotated[AsyncSession, Depends(get_main_session)],
) -> PlatformBrandingService:
    return PlatformBrandingService(
        repo=PlatformBrandingRepository(db),
        document_service=DocumentService(db),
    )


PlatformBrandingServiceDep = Annotated[
    PlatformBrandingService, Depends(get_platform_branding_service)
]
