import secrets
from abc import ABC, abstractmethod
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from config.logger import logger
from tools.config_tools import get_or_throw
from messaging.enums.notification_enums import VerificationChannel
from messaging.exceptions import (
    CodeAlreadyUsedException,
    CodeExpiredException,
    CodeNotFoundException,
)
from messaging.models.verification_code_model import VerificationCodeModel
from messaging.repositories.verification_code_repository import (
    VerificationCodeRepository,
)

EXPIRATION_MINUTES = 5


class VerificationService(ABC):
    channel: VerificationChannel

    def __init__(self, session: AsyncSession) -> None:
        self._repo = VerificationCodeRepository(session)
        self._session = session

    def _generate_code(self) -> str:
        return str(secrets.randbelow(1_000_000)).zfill(6)

    async def send_code(self, user) -> None:
        code = self._generate_code()
        record = VerificationCodeModel(
            user_id=user.id,
            channel=self.channel,
            code=code,
            expires_at=datetime.now() + timedelta(minutes=EXPIRATION_MINUTES),
        )
        await self._repo.add(record)

        if get_or_throw("ENV") == "development":
            logger.info(f"[DEV] Código de verificación — canal={self.channel.value} user_id={user.id} code={code}")
            return

        sent = await self._dispatch(user, code)
        if not sent:
            raise RuntimeError(
                f"No fue posible enviar el código por {self.channel.value}"
            )

    async def verify_code(self, user_id: int, code: str) -> None:
        try:
            record = await self._repo.verify_with_exceptions(
                user_id, code, self.channel
            )
            await self._repo.mark_consumed(record)
        except (
            CodeNotFoundException,
            CodeExpiredException,
            CodeAlreadyUsedException,
        ) as exc:
            logger.warning(
                f"Verificación fallida — user_id={user_id} canal={self.channel.value}: {exc}"
            )
            raise

    @abstractmethod
    async def _dispatch(self, user, code: str) -> bool:
        """Envía el código al destino según el canal."""
