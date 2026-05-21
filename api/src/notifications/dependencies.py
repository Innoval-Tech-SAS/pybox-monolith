from sqlalchemy.ext.asyncio import AsyncSession

from notifications.enums.notification_enums import VerificationChannel
from notifications.services.email_verification_service import EmailVerificationService
from notifications.services.sms_verification_service import SMSVerificationService
from notifications.services.verification_service import VerificationService


def get_verification_service(
    channel: VerificationChannel, session: AsyncSession
) -> VerificationService:
    if channel == VerificationChannel.EMAIL:
        return EmailVerificationService(session)
    return SMSVerificationService(session)
