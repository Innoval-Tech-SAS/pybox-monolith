from typing import cast

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.enums.auth_enums import AuthProvider
from config.seed_admin_config import SeedAdminConfig
from config.logger import logger
from countries.enums.country_enums import Nationality, UserDocumentType
from security.services.encrypt_service import encrypt_service
from security.services.password_hasher_service import PasswordHasherService
from users.enums.user_enums import UserRole, UserScope
from users.models.role_assignment_model import RoleAssignmentModel
from users.models.user_model import UserModel


async def seed_admin(session: AsyncSession) -> None:
    count = (await session.execute(select(func.count()).select_from(UserModel))).scalar()
    if count:
        return

    cfg = SeedAdminConfig()
    hasher = PasswordHasherService()

    user = UserModel(
        firstname=cfg.firstname,
        lastname=cfg.lastname,
        email=cfg.email.lower(),
        hashed_password=hasher.hash_password(cfg.password),
        phone_number=cfg.phone,
        auth_provider=AuthProvider.SELF,
        nationality=Nationality(cfg.nationality),
        document_type=UserDocumentType(cfg.doc_type),
        document_number=encrypt_service.encrypt_to_str(cfg.doc_number),
        document_number_hash=encrypt_service.hash_document(cfg.doc_number),
        is_email_verified=True,
        is_phone_verified=True,
        mfa_enabled=False,
    )
    session.add(user)
    await session.flush()

    session.add(RoleAssignmentModel(
        user_id=cast(int, user.id),
        role=UserRole.ADMIN,
        scope=UserScope.GLOBAL,
    ))
    await session.commit()
    logger.info("[seed] admin creado email=%s", user.email)
