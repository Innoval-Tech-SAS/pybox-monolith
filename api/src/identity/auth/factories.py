"""Fábrica del VerificationService según el canal (email o SMS)."""

from sqlalchemy.ext.asyncio import AsyncSession

from identity.auth.enums.notification_enums import VerificationChannel
from identity.auth.services.email_verification_service import EmailVerificationService
from identity.auth.services.sms_verification_service import SMSVerificationService
from identity.auth.services.verification_service import VerificationService


def get_verification_service(
    channel: VerificationChannel, session: AsyncSession
) -> VerificationService:
    if channel == VerificationChannel.EMAIL:
        return EmailVerificationService(session)
    return SMSVerificationService(session)
